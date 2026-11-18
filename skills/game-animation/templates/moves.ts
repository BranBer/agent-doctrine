// Move sheets: an attack as the renderer plays it. The sim lands a hero's hit on the tick the attack
// commits, so a clip is entered just before its contact pose and left at its cancel point, when the
// next swing, a step or the stance takes over. Its wind-up is never shown.

/** Times are seconds into the clip: `hit` is the contact pose, `cancel` is where control returns. */
export type Move = { clip: string; hit: number; cancel: number };

/** How long before the contact pose a move is entered: two frames of sweep into the blow. */
export const MOVE_LEAD = 1 / 30;

// Hit times are where the sword hand moves fastest in each clip (scripts/retarget-sheet.html?mark=wristr).
const TANK_LIGHT: Move[] = [
  { clip: '1H_Melee_Attack_Slice_Horizontal', hit: 0.25, cancel: 0.5 },
  { clip: '1H_Melee_Attack_Slice_Diagonal', hit: 0.38, cancel: 0.63 },
];
const TANK_HEAVY: Move = { clip: '1H_Melee_Attack_Chop', hit: 0.58, cancel: 0.95 };

/** The tank's swing for its place in the rhythm: light swings alternate, the heavy one chops. */
export function tankSwing(step: number, heavy: boolean): Move {
  return heavy ? TANK_HEAVY : TANK_LIGHT[step % TANK_LIGHT.length];
}
