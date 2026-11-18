// PROTOTYPE - NOT FOR PRODUCTION
// Posing a skeleton by where its hands should be, and baking the poses to a clip. For a move no
// animation pack has: say where each hand is at each moment and the arms follow.
// Everything here works in world space, so a skeleton's own bone axes never matter.

import * as THREE from 'three';

/** The frame of a rig that faces +z with its left along +x, as the placeholder pack's do. */
export const FORWARD = new THREE.Vector3(0, 0, 1);
export const UP = new THREE.Vector3(0, 1, 0);
export const LEFT = new THREE.Vector3(1, 0, 0);

export const easeOut = (x: number): number => 1 - (1 - x) ** 3;
export const smooth = (x: number): number => x * x * (3 - 2 * x);
export const unit = (x: number): number => THREE.MathUtils.clamp(x, 0, 1);
export const yaw = (angle: number): THREE.Quaternion => new THREE.Quaternion().setFromAxisAngle(UP, angle);

/**
 * A node between a hand's slot and what the hand holds. A clip turns it to turn the thing in the
 * hand: a wand laid along the fingers, a staff swung through the fist.
 */
export const GRIP = { l: 'Grip_l', r: 'Grip_r' } as const;

const worldQ = (o: THREE.Object3D): THREE.Quaternion => o.getWorldQuaternion(new THREE.Quaternion());
const worldP = (o: THREE.Object3D): THREE.Vector3 => o.getWorldPosition(new THREE.Vector3());

/** Sets a bone's rotation in the world. */
function face(bone: THREE.Object3D, world: THREE.Quaternion): void {
  bone.quaternion.copy(bone.parent ? worldQ(bone.parent).invert().multiply(world) : world);
}

/** Turns a bone by `by` in the world, on top of the pose it has. */
export function turn(bone: THREE.Object3D, by: THREE.Quaternion): void {
  face(bone, by.clone().multiply(worldQ(bone)));
}

/** Swings a node so that `axis`, a direction in its own frame, points along `toward` in the world. */
export function aim(node: THREE.Object3D, axis: THREE.Vector3, toward: THREE.Vector3): void {
  const now = axis.clone().applyQuaternion(worldQ(node)).normalize();
  turn(node, new THREE.Quaternion().setFromUnitVectors(now, toward.clone().normalize()));
}

/** Swings a bone so the line from it to `child` points along `to`. */
function swing(bone: THREE.Object3D, child: THREE.Object3D, to: THREE.Vector3): void {
  const from = worldP(child).sub(worldP(bone)).normalize();
  turn(bone, new THREE.Quaternion().setFromUnitVectors(from, to.clone().normalize()));
}

/**
 * Bends an arm so `end` arrives at `target`: `upper` and `lower` are its two bones, and the joint
 * between them leans toward `pole`, a direction. A target out of reach is reached toward.
 */
export function reach(upper: THREE.Object3D, lower: THREE.Object3D, end: THREE.Object3D, target: THREE.Vector3, pole: THREE.Vector3): void {
  const root = worldP(upper);
  const a = root.distanceTo(worldP(lower));
  const b = worldP(lower).distanceTo(worldP(end));
  const to = target.clone().sub(root);
  const d = THREE.MathUtils.clamp(to.length(), Math.abs(a - b) + 1e-4, (a + b) * 0.999);
  to.normalize();
  // The joint sits on a circle round the line to the target; the pole picks the point on it.
  const along = (a * a - b * b + d * d) / (2 * d);
  const out = Math.sqrt(Math.max(0, a * a - along * along));
  const side = pole.clone().addScaledVector(to, -pole.dot(to)).normalize();
  const joint = root.clone().addScaledVector(to, along).addScaledVector(side, out);
  swing(upper, lower, joint.clone().sub(root));
  swing(lower, end, root.clone().addScaledVector(to, d).sub(joint));
}

/** A hand that holds something, read at rest: which way it points, which way its palm faces, and where its grip is. */
export type Grip = { wrist: THREE.Object3D; points: THREE.Vector3; palm: THREE.Vector3; rest: THREE.Quaternion; toGrip: THREE.Vector3 };

/** Reads a hand from the node things are held at: its parent is the hand bone, and that bone's parent the wrist. */
export function gripOf(slot: THREE.Object3D): Grip {
  const hand = slot.parent!;
  const wrist = hand.parent!;
  const points = worldP(hand).sub(worldP(wrist)).normalize();
  const off = worldP(slot).sub(worldP(hand));
  const palm = off.addScaledVector(points, -off.dot(points)).normalize();
  return { wrist, points, palm, rest: worldQ(wrist), toGrip: worldP(slot).sub(worldP(wrist)) };
}

/** A frame from the way a hand points and the way its palm faces. */
export function handFrame(points: THREE.Vector3, palm: THREE.Vector3): THREE.Quaternion {
  const x = points.clone().normalize();
  const z = palm.clone().addScaledVector(x, -palm.dot(x)).normalize();
  return new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(x, z.clone().cross(x), z));
}

/** Puts a hand's grip at `at`, pointing along `points` with its palm facing `palm`, and bends the arm to it. */
export function hold(upper: THREE.Object3D, lower: THREE.Object3D, g: Grip, at: THREE.Vector3, points: THREE.Vector3, palm: THREE.Vector3, pole: THREE.Vector3): void {
  const carried = handFrame(points, palm).multiply(handFrame(g.points, g.palm).invert());
  reach(upper, lower, g.wrist, at.clone().sub(g.toGrip.clone().applyQuaternion(carried)), pole);
  face(g.wrist, carried.multiply(g.rest));
}

/**
 * Bakes poses to a clip. Every bone starts each frame from the pose it has now; `pose(t)` then sets
 * them for time `t`, and each bone's rotation is keyed `fps` times a second.
 */
export function bake(name: string, duration: number, bones: THREE.Object3D[], pose: (t: number) => void, fps = 60): THREE.AnimationClip {
  const start = bones.map((b) => b.quaternion.clone());
  const frames = Math.max(1, Math.round(duration * fps));
  const times = Array.from({ length: frames + 1 }, (_, f) => (duration * f) / frames);
  const keys = bones.map(() => [] as number[]);
  for (const t of times) {
    bones.forEach((b, i) => b.quaternion.copy(start[i]));
    pose(t);
    bones.forEach((b, i) => keys[i].push(...b.quaternion.toArray()));
  }
  bones.forEach((b, i) => b.quaternion.copy(start[i]));
  return new THREE.AnimationClip(name, duration, bones.map((b, i) => new THREE.QuaternionKeyframeTrack(`${b.name}.quaternion`, times, keys[i])));
}
