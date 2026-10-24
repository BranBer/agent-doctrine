import * as THREE from 'three';

// A test model in the glTF frame (+Y up, nose toward +Z): 1 wide (x), 2 tall (y), 4 long (z),
// with a red cap at the nose so the side and top views are not symmetric.
export default function box() {
  const root = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(1, 2, 4), new THREE.MeshStandardMaterial({ color: '#3D63DD' }));
  body.position.y = 1;
  const cap = new THREE.Mesh(new THREE.BoxGeometry(1, 0.5, 0.5), new THREE.MeshStandardMaterial({ color: '#E64F8E' }));
  cap.position.set(0, 2.25, 1.75);
  root.add(body, cap);
  return root;
}
