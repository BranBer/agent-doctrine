import * as THREE from 'three';

// A test model for the symmetry check, in the glTF frame: a 2 m wide body with a roof rack, a mirror on each side, and
// an antenna on its right that the model declares one-sided. rackX moves the rack off the centre line, the fault the
// check exists for; mirrorGap moves the right mirror out of line with the left one.
export default function racked({ rackX = 0, mirrorGap = 0 } = {}) {
  const steel = new THREE.MeshStandardMaterial({ color: '#8C9298' });
  const box = (name, [w, h, d], [x, y, z]) => {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), steel);
    mesh.name = name;
    mesh.position.set(x, y, z);
    return mesh;
  };
  const antenna = box('antenna', [0.04, 0.8, 0.04], [-0.7, 1.6, -1.5]);
  antenna.userData.oneSided = true;
  const root = new THREE.Group();
  root.add(
    box('body', [2, 1.2, 4], [0, 0.6, 0]),
    box('roof-rack', [1.2, 0.15, 1.5], [rackX, 1.275, 0]),
    box('mirror-left', [0.2, 0.15, 0.1], [1.1, 0.9, 0.8]),
    box('mirror-right', [0.2, 0.15, 0.1], [-1.1 - mirrorGap, 0.9, 0.8]),
    antenna,
  );
  return root;
}
