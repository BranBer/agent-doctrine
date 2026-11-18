import assert from 'node:assert/strict';
import { test } from 'node:test';
import * as THREE from 'three';
import { plan, retargetClips, socket } from './retarget.ts';

/** A two-bone arm hanging off a root: `axis` is the way the arm points at rest. */
function arm(names: [string, string, string], axis: THREE.Vector3, roll: number): THREE.Object3D {
  const root = new THREE.Group();
  const [a, b, c] = names.map((n) => Object.assign(new THREE.Bone(), { name: n }));
  // A rig's local axes are arbitrary: roll the upper bone about its own length.
  a.quaternion.setFromAxisAngle(axis, roll);
  const along = axis.clone().applyQuaternion(a.quaternion.clone().invert());
  b.position.copy(along);
  c.position.copy(along);
  a.position.set(0, 1, 0);
  root.add(a.add(b.add(c)));
  return root;
}

const direction = (root: THREE.Object3D, from: string, to: string): THREE.Vector3 => {
  root.updateMatrixWorld(true);
  const p = (n: string) => root.getObjectByName(n)!.getWorldPosition(new THREE.Vector3());
  return p(to).sub(p(from)).normalize();
};

test('a bend in the source appears as the same world-space bend in a target with another rest pose, roll and facing', () => {
  // Source: arm out to the side (T-pose), facing +z. Target: arm hanging down (A-pose), facing +x.
  const source = arm(['up', 'low', 'tip'], new THREE.Vector3(1, 0, 0), 0);
  const target = arm(['Arm', 'ForeArm', 'Hand'], new THREE.Vector3(0, -1, 0), 1.1);
  const bend = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), -Math.PI / 2);
  const rest = source.getObjectByName('low')!.quaternion;
  const clip = new THREE.AnimationClip('bend', 1, [
    new THREE.QuaternionKeyframeTrack('low.quaternion', [0, 1], [...rest.toArray(), ...rest.clone().multiply(bend).toArray()]),
  ]);
  const matched = plan(source, target, [['up', 'Arm'], ['low', 'ForeArm']], Math.PI / 2);
  const [made] = retargetClips(matched, [clip]);
  const held = socket(matched, 'tip');

  const pose = (root: THREE.Object3D, c: THREE.AnimationClip, time: number) => {
    const mixer = new THREE.AnimationMixer(root);
    mixer.clipAction(c).play();
    mixer.setTime(time);
  };
  pose(source, clip, 0.999);
  pose(target, made, 0.999);
  // Source forearm swings from +x toward +z (forward); turned a quarter, the target's must point at +x (its forward).
  const want = direction(source, 'low', 'tip').applyAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI / 2);
  const got = direction(target, 'ForeArm', 'Hand');
  assert.ok(got.distanceTo(want) < 1e-3, `forearm points ${got.toArray()} not ${want.toArray()}`);
  // Something carried at the source's tip rides the target's forearm to the same place: the target's own tip.
  const carrier = new THREE.Group();
  carrier.position.copy(held.position);
  target.getObjectByName(held.bone)!.add(carrier);
  target.updateMatrixWorld(true);
  const tip = target.getObjectByName('Hand')!.getWorldPosition(new THREE.Vector3());
  assert.equal(held.bone, 'ForeArm');
  assert.ok(carrier.getWorldPosition(new THREE.Vector3()).distanceTo(tip) < 1e-3, 'the carried thing is off the hand');
  // And the upper arm took the source's rest direction, turned: +x becomes -z.
  const upper = direction(target, 'Arm', 'ForeArm');
  assert.ok(upper.distanceTo(new THREE.Vector3(0, 0, -1)) < 1e-3, `upper arm points ${upper.toArray()}`);
});
