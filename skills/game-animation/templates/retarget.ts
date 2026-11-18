// Plays one skeleton's clips on another with different bone names, rest pose and facing.
// Each mapped bone copies the source bone's turn away from its rest pose, in world space,
// so the two skeletons' local axes never have to agree.

import * as THREE from 'three';
import { clone as cloneSkinned } from 'three/addons/utils/SkeletonUtils.js';

/** Source bone name to target bone name, parents before children, as GLTFLoader names them. */
export type BoneMap = readonly (readonly [string, string])[];

/** KayKit's rig onto a Mixamo-named one. Neck, shoulders, the middle spine bone and all but the middle fingers keep
    their rest pose. The middle finger stands in for KayKit's one hand bone, so each hand has a direction to align. */
export const KAYKIT_TO_MIXAMO: BoneMap = [
  ['hips', 'mixamorigHips'],
  ['spine', 'mixamorigSpine'],
  ['chest', 'mixamorigSpine2'],
  ['head', 'mixamorigHead'],
  ['upperarml', 'mixamorigLeftArm'],
  ['lowerarml', 'mixamorigLeftForeArm'],
  ['wristl', 'mixamorigLeftHand'],
  ['handl', 'mixamorigLeftHandMiddle1'],
  ['upperarmr', 'mixamorigRightArm'],
  ['lowerarmr', 'mixamorigRightForeArm'],
  ['wristr', 'mixamorigRightHand'],
  ['handr', 'mixamorigRightHandMiddle1'],
  ['upperlegl', 'mixamorigLeftUpLeg'],
  ['lowerlegl', 'mixamorigLeftLeg'],
  ['footl', 'mixamorigLeftFoot'],
  ['toesl', 'mixamorigLeftToeBase'],
  ['upperlegr', 'mixamorigRightUpLeg'],
  ['lowerlegr', 'mixamorigRightLeg'],
  ['footr', 'mixamorigRightFoot'],
  ['toesr', 'mixamorigRightToeBase'],
];

type Pair = { s: THREE.Object3D; t: THREE.Object3D; fix: THREE.Quaternion };

/** Two skeletons read at rest and matched up, ready to retarget clips or place a carried prop. */
/** `lift` is how much higher the target's hips ride; `size` is how much bigger its skeleton is. */
export type Plan = { src: THREE.Object3D; pairs: Pair[]; turn: THREE.Quaternion; lift: number; size: number };

const isUnder = (o: THREE.Object3D, ancestor: THREE.Object3D): boolean => {
  for (let p = o.parent; p; p = p.parent) if (p === ancestor) return true;
  return false;
};
const worldQ = (o: THREE.Object3D): THREE.Quaternion => o.getWorldQuaternion(new THREE.Quaternion());
const worldP = (o: THREE.Object3D): THREE.Vector3 => o.getWorldPosition(new THREE.Vector3());

/**
 * Matches `source`'s bones to `target`'s by `map`, both read at rest. `yaw` turns the source's facing
 * to the target's: a source facing +z onto a target facing +x is +90 degrees.
 */
export function plan(source: THREE.Object3D, target: THREE.Object3D, map: BoneMap, yaw: number): Plan {
  const src = cloneSkinned(source);
  const dst = cloneSkinned(target);
  src.updateMatrixWorld(true);
  dst.updateMatrixWorld(true);
  const turn = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
  const unturn = turn.clone().invert();

  const found = map.flatMap(([a, b]) => {
    const s = src.getObjectByName(a);
    const t = dst.getObjectByName(b);
    return s && t ? [{ s, t }] : [];
  });
  if (!found.length) throw new Error('retarget: no bone in the map exists in both skeletons');

  // At rest the target must first take the source's rest pose: turn each bone so it points at its
  // mapped child the way the source's does. A bone with no mapped child keeps its parent's turn.
  const aligned = new Map<THREE.Object3D, THREE.Quaternion>();
  const pairs: Pair[] = found.map(({ s, t }, i) => {
    const child = found.slice(i + 1).find((c) => isUnder(c.s, s) && isUnder(c.t, t));
    const parent = [...found.slice(0, i)].reverse().find((p) => isUnder(s, p.s));
    let align = parent ? aligned.get(parent.t)!.clone() : new THREE.Quaternion();
    if (child) {
      const from = worldP(child.t).sub(worldP(t)).normalize();
      const to = worldP(child.s).sub(worldP(s)).normalize().applyQuaternion(turn);
      align = new THREE.Quaternion().setFromUnitVectors(from, to);
    }
    aligned.set(t, align);
    // target world = turn * sourceWorld(t) * fix
    const fix = worldQ(s).invert().multiply(unturn).multiply(align).multiply(worldQ(t));
    return { s, t, fix };
  });
  const lift = worldP(pairs[0].t).y / Math.max(1e-6, worldP(pairs[0].s).y);
  // The farthest two mapped bones: head to toe on a standing figure, whichever way it stands.
  const span = (side: 's' | 't'): number => {
    const at = pairs.map((x) => worldP(x[side]));
    return Math.max(...at.flatMap((a) => at.map((b) => a.distanceTo(b))));
  };
  return { src, pairs, turn, lift, size: span('t') / Math.max(1e-6, span('s')) };
}

/**
 * Where something the source carries on `sourceNode` (a hand slot) sits on the target: the target bone's
 * name and the carrier's place in that bone's own frame, sized to the target.
 */
export function socket(p: Plan, sourceNode: string): { bone: string; position: THREE.Vector3; quaternion: THREE.Quaternion; scale: number } {
  const node = p.src.getObjectByName(sourceNode);
  const pair = node && [...p.pairs].reverse().find((x) => isUnder(node, x.s));
  if (!node || !pair) throw new Error(`retarget: ${sourceNode} is not under a mapped bone`);
  // In the pose both share, the bone's world turn is turn * sourceWorld * fix; the yaw cancels out.
  const toBone = worldQ(pair.s).multiply(pair.fix).invert();
  return {
    bone: pair.t.name,
    position: worldP(node).sub(worldP(pair.s)).multiplyScalar(p.size).applyQuaternion(toBone),
    quaternion: toBone.clone().multiply(worldQ(node)),
    scale: p.size,
  };
}

/**
 * Returns `clips` rewritten for the plan's target: one rotation track per mapped bone and a position
 * track for the first mapped bone (the hips), sampled at `fps`.
 */
export function retargetClips({ src, pairs, turn, lift }: Plan, clips: THREE.AnimationClip[], fps = 30): THREE.AnimationClip[] {
  const hips = pairs[0];
  const hipsRest = hips.t.position.clone();
  const srcHipsRest = worldP(hips.s);
  const hipsParent = hips.t.parent ? worldQ(hips.t.parent).invert() : new THREE.Quaternion();

  const mixer = new THREE.AnimationMixer(src);
  const out = clips.map((clip) => {
    mixer.stopAllAction();
    mixer.clipAction(clip).reset().play();
    const frames = Math.max(1, Math.round(clip.duration * fps));
    const times = new Float32Array(frames + 1);
    const rot = pairs.map(() => new Float32Array((frames + 1) * 4));
    const pos = new Float32Array((frames + 1) * 3);
    for (let f = 0; f <= frames; f++) {
      const time = Math.min(f / fps, clip.duration);
      times[f] = time;
      // The last sample sits a hair before the end, so a looping action does not wrap to its start.
      mixer.setTime(Math.min(time, clip.duration - 1e-4));
      src.updateMatrixWorld(true);
      pairs.forEach(({ s, t, fix }, i) => {
        const world = turn.clone().multiply(worldQ(s)).multiply(fix);
        t.quaternion.copy(t.parent ? worldQ(t.parent).invert().multiply(world) : world);
        t.quaternion.toArray(rot[i], f * 4);
      });
      const move = worldP(hips.s).sub(srcHipsRest).applyQuaternion(turn).multiplyScalar(lift).applyQuaternion(hipsParent);
      hipsRest.clone().add(move).toArray(pos, f * 3);
    }
    mixer.uncacheClip(clip);
    const tracks: THREE.KeyframeTrack[] = pairs.map(({ t }, i) => new THREE.QuaternionKeyframeTrack(`${t.name}.quaternion`, times, rot[i]));
    tracks.push(new THREE.VectorKeyframeTrack(`${hips.t.name}.position`, times, pos));
    return new THREE.AnimationClip(clip.name, clip.duration, tracks);
  });
  return out;
}
