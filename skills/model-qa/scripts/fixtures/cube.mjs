import * as THREE from 'three';

// A 1 m cube: its diagonal is 1.73 times its longest side, the case a hero camera framed on the
// longest side crops.
export default function cube() {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial({ color: '#4C5664' }));
  mesh.position.y = 0.5;
  return mesh;
}
