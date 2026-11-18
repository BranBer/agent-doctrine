// PROTOTYPE - NOT FOR PRODUCTION
// The streak a swung thing leaves behind it: the strip its outer end has just swept, fading out.
// Drawn over everything, because at the game's size and angle the swing itself is often hidden.

import * as THREE from 'three';

/** How many frames of the sweep it keeps, how long each lasts, and how far back from the tip the strip reaches (0 to 1). */
const TRAIL = { samples: 14, seconds: 0.18, back: 0.6 };

export class Trail {
  readonly mesh: THREE.Mesh;
  private readonly color: THREE.Color;
  private swept: { tip: THREE.Vector3; back: THREE.Vector3; age: number }[] = [];

  constructor(color: number) {
    this.color = new THREE.Color(color);
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(TRAIL.samples * 6), 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(TRAIL.samples * 6), 3));
    // Two points a sample, joined to the next sample's two.
    const index: number[] = [];
    for (let i = 0; i < TRAIL.samples - 1; i++) index.push(i * 2, i * 2 + 1, i * 2 + 2, i * 2 + 1, i * 2 + 3, i * 2 + 2);
    geometry.setIndex(index);
    // Additive, so a sample fading to black fades out.
    const material = new THREE.MeshBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, depthTest: false, depthWrite: false, toneMapped: false });
    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.frustumCulled = false;
    this.mesh.renderOrder = 5;
  }

  /** Each frame: where the swung thing's tip and its held end are in the world. While `sweeping` the strip grows; otherwise it fades. */
  step(tip: THREE.Vector3, held: THREE.Vector3, sweeping: boolean, dt: number): void {
    for (const s of this.swept) s.age += dt;
    this.swept = this.swept.filter((s) => s.age < TRAIL.seconds);
    if (sweeping) this.swept.unshift({ tip: tip.clone(), back: tip.clone().lerp(held, TRAIL.back), age: 0 });
    this.swept.length = Math.min(this.swept.length, TRAIL.samples);
    const position = this.mesh.geometry.getAttribute('position') as THREE.BufferAttribute;
    const color = this.mesh.geometry.getAttribute('color') as THREE.BufferAttribute;
    this.swept.forEach((s, i) => {
      const k = (1 - s.age / TRAIL.seconds) ** 2;
      position.setXYZ(i * 2, s.tip.x, s.tip.y, s.tip.z);
      position.setXYZ(i * 2 + 1, s.back.x, s.back.y, s.back.z);
      color.setXYZ(i * 2, this.color.r * k, this.color.g * k, this.color.b * k);
      // The strip is brightest at the tip.
      color.setXYZ(i * 2 + 1, this.color.r * k * 0.25, this.color.g * k * 0.25, this.color.b * k * 0.25);
    });
    position.needsUpdate = true;
    color.needsUpdate = true;
    this.mesh.geometry.setDrawRange(0, Math.max(0, this.swept.length - 1) * 6);
  }
}
