// PROTOTYPE - NOT FOR PRODUCTION
import assert from 'node:assert/strict';
import { test } from 'node:test';
import * as THREE from 'three';
import { bake, gripOf, hold, reach } from './pose.ts';

/** An arm along +x under a turned parent: shoulder, elbow, wrist, hand, and a slot in the palm. */
function arm(): { root: THREE.Object3D; upper: THREE.Object3D; lower: THREE.Object3D; wrist: THREE.Object3D; slot: THREE.Object3D } {
  const make = (name: string, x: number, parent?: THREE.Object3D): THREE.Object3D => {
    const o = new THREE.Object3D();
    o.name = name;
    o.position.x = x;
    parent?.add(o);
    return o;
  };
  const root = make('root', 0);
  root.rotation.set(0.3, 0.8, -0.2);
  const upper = make('upper', 0.2, root);
  const lower = make('lower', 0.3, upper);
  const wrist = make('wrist', 0.25, lower);
  const hand = make('hand', 0.07, wrist);
  const slot = make('slot', 0.1, hand);
  slot.position.z = -0.05;
  root.updateMatrixWorld(true);
  return { root, upper, lower, wrist, slot };
}
const at = (o: THREE.Object3D): THREE.Vector3 => o.getWorldPosition(new THREE.Vector3());

test('an arm bends so its end arrives at a target in reach, and stretches toward one out of reach', () => {
  const { upper, lower, wrist } = arm();
  const target = at(upper).add(new THREE.Vector3(0.1, 0.3, 0.25));
  reach(upper, lower, wrist, target, new THREE.Vector3(0, -1, 0));
  assert.ok(at(wrist).distanceTo(target) < 1e-3, 'the wrist is on the target');
  assert.ok(at(lower).y < at(upper).y + 0.2, 'the elbow leans toward the pole');
  const far = at(upper).add(new THREE.Vector3(0, 0, 5));
  reach(upper, lower, wrist, far, new THREE.Vector3(0, -1, 0));
  assert.ok(Math.abs(at(wrist).distanceTo(at(upper)) - 0.55) < 2e-3, 'the arm is straight');
  assert.ok(at(wrist).sub(at(upper)).normalize().z > 0.999, 'and points at the target');
});

test('a held grip arrives where it is put, pointing and facing as asked, and the pose bakes to a clip', () => {
  const { upper, lower, wrist, slot } = arm();
  const g = gripOf(slot);
  const target = at(upper).add(new THREE.Vector3(-0.1, 0.1, 0.4));
  const points = new THREE.Vector3(0, 0, 1);
  const palm = new THREE.Vector3(-1, 0, 0);
  const clip = bake('Held', 0.1, [upper, lower, wrist], () => hold(upper, lower, g, target, points, palm, new THREE.Vector3(0, -1, 0)));
  assert.ok(at(upper).distanceTo(at(lower)) > 0, 'the arm is left as it was found');
  assert.equal(clip.tracks.length, 3);
  assert.equal(clip.tracks[0].name, 'upper.quaternion');
  hold(upper, lower, g, target, points, palm, new THREE.Vector3(0, -1, 0));
  assert.ok(at(slot).distanceTo(target) < 1e-3, 'the grip is on the target');
  const pointing = at(slot.parent!).sub(at(wrist)).normalize();
  assert.ok(pointing.dot(points) > 0.999, 'the hand points the way it was asked to');
  // The slot sits on the palm side of the hand.
  const off = at(slot).sub(at(slot.parent!));
  assert.ok(off.addScaledVector(points, -off.dot(points)).normalize().dot(palm) > 0.999, 'and its palm faces the way it was asked to');
});
