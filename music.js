/* Pizza Magna — 8-bit / lo-fi Italian music, synthesised with Web Audio (no audio files).
   Four voices like an old console: square lead (25% duty), triangle bass, soft square harmony, noise drums,
   through a gentle low-pass filter with a slow "tape" wobble for the lo-fi feel.
   The tunes are original compositions in the style of Neapolitan classics, the tarantella and Verdi's "La donna è mobile",
   plus a swaying 1950s crooner tune and a slow romantic ballad.
   The last four are public-domain classics, melody as written: converted from ABC by tools/abc2music.py.
   Notation: one token per step (an eighth note); "-" holds the previous note, "." is silence.
   Drums: k = kick, s = snare, h = hat, . = nothing. */
const MUSIC = (() => {
  const SONGS = [
    { id: 'tarantella', title: 'Tarantella della Pizza', bpm: 380, beat: 6, loops: 2, trem: false, parts: 'AABA',
      A: {
        lead: 'E5 E5 E5 E5 F5 E5 | D5 D5 D5 D5 E5 D5 | C5 C5 C5 C5 D5 C5 | B4 C5 B4 A4 - - | A4 B4 C5 D5 E5 F5 | E5 - D5 C5 B4 A4 | G#4 A4 B4 E4 G#4 B4 | A4 - - . . .',
        bass: 'A2 - - E3 - - | G2 - - D3 - - | F2 - - C3 - - | E2 - - E3 - - | A2 - - E3 - - | D3 - - A2 - - | E2 - - B2 - - | A2 - - E2 - -',
        harm: 'C5 - - C5 - - | B4 - - B4 - - | A4 - - A4 - - | G#4 - - G#4 - - | C5 - - C5 - - | A4 - - F4 - - | E4 - - D4 - - | C4 - - . . .' },
      B: {
        lead: 'G5 G5 G5 G5 A5 G5 | F5 F5 F5 F5 G5 F5 | E5 E5 E5 E5 F5 E5 | D5 E5 D5 C5 - - | C5 D5 E5 F5 G5 A5 | G5 - F5 E5 D5 C5 | B4 C5 D5 E5 D5 B4 | C5 - - E5 - -',
        bass: 'C3 - - G2 - - | F2 - - C3 - - | C3 - - G2 - - | G2 - - D3 - - | A2 - - E3 - - | F2 - - C3 - - | G2 - - D3 - - | C3 - - E2 - -',
        harm: 'E5 - - E5 - - | C5 - - C5 - - | C5 - - C5 - - | B4 - - B4 - - | E5 - - E5 - - | C5 - - A4 - - | D5 - - B4 - - | E5 - - G#4 - -' },
      drums: 'k . h s . h' },
    { id: 'serenata', title: 'Serenata al Forno', bpm: 150, beat: 6, loops: 2, trem: true, parts: 'A',
      A: {
        lead: 'A4 - D5 - E5 - | F5 - - - E5 D5 | E5 - A4 - - - | . . A4 - B4 C#5 | D5 - F5 - A5 - | G5 - - - F5 E5 | F5 - D5 - - - | . . D5 - E5 F5 | G5 - - - Bb5 A5 | G5 - F5 - E5 - | F5 - - - A4 - | D5 - - - . . | E5 - - - G5 F5 | E5 - D5 - C#5 - | D5 - - - - - | . . . . . .',
        bass: 'D2 - A2 - D3 - | D2 - A2 - D3 - | A1 - E2 - A2 - | A1 - E2 - G2 - | D2 - A2 - D3 - | G1 - D2 - G2 - | D2 - A2 - D3 - | D2 - A2 - C3 - | G1 - D2 - G2 - | C2 - G2 - C3 - | F1 - C2 - F2 - | Bb1 - F2 - Bb2 - | G1 - D2 - G2 - | A1 - E2 - A2 - | D2 - A2 - D3 - | D2 - - - - -',
        harm: 'F4 - - - - - | A4 - - - - - | C#4 - - - - - | E4 - - - - - | F4 - - - - - | Bb4 - - - - - | A4 - - - - - | F#4 - - - - - | Bb4 - - - - - | C5 - - - - - | A4 - - - - - | F4 - - - - - | Bb4 - - - - - | C#5 - - - - - | A4 - - - - - | . . . . . .' },
      drums: 'k . h . h .' },
    { id: 'funicolare', title: 'Funicolare', bpm: 330, beat: 6, loops: 2, trem: false, parts: 'A',
      A: {
        lead: 'G4 - C5 C5 - E5 | G5 - - E5 - C5 | D5 - F5 F5 - A5 | G5 - - . . . | A5 - G5 F5 - E5 | D5 - E5 F5 - D5 | E5 - C5 D5 - B4 | C5 - - . . . | E5 E5 E5 F5 E5 D5 | E5 - - C5 - - | F5 F5 F5 G5 F5 E5 | F5 - - D5 - - | G5 - E5 F5 - D5 | E5 - C5 D5 - B4 | C5 - E5 D5 - B4 | C5 - - . . .',
        bass: 'C3 - - G2 - - | C3 - - G2 - - | G2 - - D3 - - | G2 - - D3 - - | F2 - - C3 - - | G2 - - D3 - - | C3 - - G2 - - | C3 - - G2 - - | C3 - - G2 - - | C3 - - G2 - - | G2 - - D3 - - | G2 - - D3 - - | C3 - - G2 - - | F2 - - C3 - - | G2 - - D3 - - | C3 - - G2 - -',
        harm: 'E4 - - E4 - - | E4 - - G4 - - | B4 - - B4 - - | B4 - - . . . | C5 - - A4 - - | B4 - - B4 - - | G4 - - F4 - - | E4 - - . . . | G4 - - G4 - - | G4 - - G4 - - | B4 - - B4 - - | B4 - - B4 - - | E5 - - B4 - - | C5 - - A4 - - | G4 - - F4 - - | E4 - - . . .' },
      drums: 'k . h s . h' },
    { id: 'golfo', title: 'Sole sul Golfo', bpm: 200, beat: 8, loops: 3, trem: true, parts: 'A',
      A: {
        lead: 'C5 - - - A4 - C5 - | F5 - - - E5 - D5 - | C5 - - - Bb4 - A4 - | G4 - - - - - . . | A4 - - - C5 - F5 - | A5 - - - G5 - F5 - | E5 - - - D5 - E5 - | F5 - - - - - . .',
        bass: 'F2 - C3 - F2 - C3 - | Bb1 - F2 - Bb1 - F2 - | F2 - C3 - F2 - C3 - | C2 - G2 - C2 - G2 - | F2 - C3 - F2 - C3 - | D2 - A2 - D2 - A2 - | C2 - G2 - C2 - G2 - | F2 - C3 - F2 - - -',
        harm: 'A4 - - - - - - - | D5 - - - - - - - | A4 - - - - - - - | E4 - - - - - - - | F4 - - - - - - - | F5 - - - - - - - | C5 - - - Bb4 - - - | A4 - - - - - . .' },
      drums: 'k . h . s . h .' },
    { id: 'mobile', title: 'La Pizza è Mobile', bpm: 330, beat: 6, loops: 2, trem: false, parts: 'A',
      A: {
        lead: 'C5 C5 C5 E5 - D5 | A4 - - . . . | D5 D5 D5 F5 - E5 | Bb4 - - . . . | E5 F5 G5 A5 G5 F5 | E5 D5 C5 Bb4 A4 G4 | F4 A4 C5 E5 - D5 | C5 - - . . . | G5 G5 G5 Bb5 - A5 | F5 - - . . . | A5 A5 A5 C6 - Bb5 | G5 - - . . . | F5 G5 A5 Bb5 A5 G5 | F5 E5 D5 C5 Bb4 A4 | G4 Bb4 D5 C5 - E4 | F4 - - . . .',
        bass: 'F2 C3 C3 F2 C3 C3 | F2 C3 C3 F2 C3 C3 | C2 G2 Bb2 C2 G2 Bb2 | C2 G2 Bb2 C2 G2 Bb2 | F2 C3 C3 F2 C3 C3 | C2 G2 Bb2 C2 G2 Bb2 | F2 C3 C3 F2 C3 C3 | F2 C3 C3 F2 C3 C3 | C2 G2 Bb2 C2 G2 Bb2 | F2 C3 C3 F2 C3 C3 | F2 C3 C3 F2 C3 C3 | C2 G2 G2 C2 G2 G2 | Bb1 F2 F2 Bb1 F2 F2 | F2 C3 C3 F2 C3 C3 | C2 G2 Bb2 C2 G2 Bb2 | F2 C3 C3 F2 - -',
        harm: 'A4 - - - - - | A4 - - - - - | Bb4 - - - - - | Bb4 - - - - - | A4 - - - - - | Bb4 - - - - - | A4 - - - - - | A4 - - - - - | Bb4 - - - - - | A4 - - - - - | A4 - - - - - | G4 - - - - - | D5 - - - - - | A4 - - - - - | Bb4 - - - - - | A4 - - . . .' },
      drums: 'k . . h . .' },
    { id: 'positano', title: 'Pomeriggio a Positano', bpm: 140, beat: 8, loops: 3, trem: true, parts: 'A',   // a quiet afternoon by the sea
      A: {
        lead: 'B4 - - - D5 - G5 - | F#5 - - - E5 - D5 - | C5 - - - E5 - A5 - | G5 - - - - - . . | E5 - - - G5 - B5 - | A5 - - - G5 - E5 - | D5 - - - C5 - A4 - | G4 - - - - - . .',
        bass: 'G2 - D3 - G2 - D3 - | D2 - A2 - D2 - A2 - | C2 - G2 - C2 - G2 - | G2 - D3 - G2 - D3 - | E2 - B2 - E2 - B2 - | C2 - G2 - C2 - G2 - | D2 - A2 - D2 - A2 - | G2 - D3 - G2 - - -',
        harm: 'D4 - - - - - - - | F#4 - - - - - - - | E4 - - - - - - - | D4 - - - - - - - | G4 - - - - - - - | E4 - - - - - - - | F#4 - - - - - - - | B3 - - - - - . .' },
      drums: 'k . . . h . . .' },
    { id: 'siesta', title: 'Siesta in Piazza', bpm: 120, beat: 6, loops: 3, trem: false, parts: 'A',   // a slow, sleepy waltz
      A: {
        lead: 'A4 - C5 - F5 - | E5 - - - D5 - | C5 - - - A4 - | C5 - - - - - | D5 - F5 - Bb5 - | A5 - - - G5 - | F5 - - - E5 - | F5 - - - . .',
        bass: 'F2 - A2 - C3 - | C2 - E2 - G2 - | F2 - A2 - C3 - | C2 - E2 - G2 - | Bb1 - D2 - F2 - | F2 - A2 - C3 - | C2 - E2 - G2 - | F2 - - - . .',
        harm: 'C4 - - - - - | E4 - - - - - | C4 - - - - - | E4 - - - - - | D4 - - - - - | C4 - - - - - | E4 - - - - - | A3 - - - . .' },
      drums: 'k . . . h .' },
    { id: 'luna', title: 'Luna sulla Pizza', bpm: 300, beat: 6, loops: 2, trem: false, parts: 'A',   // a swaying crooner tune, moon over the bay
      A: {
        lead: 'G4 - C5 - E5 - | G5 - - E5 - C5 | D5 - - - - - | . . G4 A4 B4 C5 | D5 - F5 - A5 - | G5 - - F5 - D5 | E5 - - - - - | . . E5 F5 E5 D5 | C5 - E5 - G5 - | C6 - - B5 - A5 | G5 - - E5 - C5 | A4 - - - - - | D5 - - F5 - - | E5 - - C5 - - | D5 - - B4 - - | C5 - - - . .',
        bass: 'C3 - - G2 - - | C3 - - G2 - - | G2 - - D3 - - | G2 - - D3 - - | G2 - - D3 - - | G2 - - D3 - - | C3 - - G2 - - | C3 - - G2 - - | C3 - - G2 - - | A2 - - E3 - - | F2 - - C3 - - | F2 - - C3 - - | G2 - - D3 - - | C3 - - A2 - - | G2 - - D3 - - | C3 - - G2 - -',
        harm: 'E4 - - - - - | E4 - - - - - | B4 - - - - - | B4 - - - - - | B4 - - - - - | B4 - - - - - | G4 - - - - - | G4 - - - - - | E4 - - - - - | E4 - - - - - | A4 - - - - - | A4 - - - - - | B4 - - - - - | G4 - - - - - | F4 - - - - - | E4 - - . . .' },
      drums: 'k . h s . h' },
    { id: 'bello', title: "L'Amore più Bello", bpm: 160, beat: 8, loops: 2, trem: false, parts: 'A',   // a slow romantic ballad in E minor
      A: {
        lead: 'E5 - - - D5 - B4 - | C5 - - - B4 - A4 - | B4 - - - G4 - E4 - | F#4 - - - - - . . | G4 - A4 - B4 - E5 - | D5 - - - C5 - B4 - | A4 - - - B4 - C5 - | B4 - - - - - . . | E5 - - - F#5 - G5 - | A5 - - - G5 - F#5 - | G5 - - - E5 - C5 - | D5 - - - - - . . | C5 - - - B4 - A4 - | B4 - - - G4 - F#4 - | E4 - - - - - - - | . . . . . . . .',
        bass: 'E2 - B2 - E3 - B2 - | A2 - E3 - A2 - E3 - | E2 - B2 - E3 - B2 - | B1 - F#2 - B2 - F#2 - | G2 - D3 - G2 - D3 - | G2 - D3 - G2 - D3 - | A2 - E3 - A2 - E3 - | B1 - F#2 - B2 - F#2 - | C2 - G2 - C3 - G2 - | D2 - A2 - D3 - A2 - | E2 - B2 - E3 - B2 - | B1 - F#2 - B2 - F#2 - | A2 - E3 - A2 - E3 - | B1 - F#2 - B2 - F#2 - | E2 - B2 - E3 - B2 - | E2 - - - - - - -',
        harm: 'G4 - - - - - - - | E4 - - - - - - - | G4 - - - - - - - | D#4 - - - - - - - | B4 - - - - - - - | B4 - - - - - - - | C5 - - - - - - - | D#5 - - - - - - - | E5 - - - - - - - | F#4 - - - - - - - | G4 - - - - - - - | F#4 - - - - - - - | E4 - - - - - - - | D#4 - - - - - - - | G4 - - - - - - - | . . . . . . . .' },
      drums: 'k . . . h . . .' },
    { id: 'verdi', title: "La donna è mobile (Verdi)", bpm: 276, beat: 6, loops: 2, trem: false, parts: 'A',   // public domain: melody as written (abcnotation.com)
      A: {
        lead: 'A4 - A4 - A4 - C5 Bb4 G4 - - - G4 - G4 - G4 - Bb4 A4 F4 - - - A4 - G4 - F4 - F4 E4 E4 - - - G4 - F4 - D4 - D4 C4 C4 - - - A4 - A4 - A4 - C5 Bb4 G4 - - - G4 - G4 - G4 - Bb4 A4 F4 - - - A4 - G4 - F4 - F4 E4 E4 - - - G4 - F4 - D4 - D4 C4 C4 - - - G4 A4 G4 - G4 - C5 - G4 - - - A4 Bb4 A4 - A4 - D5 - A4 - - - C5 D5 C5 - C5 - D5 - - - C5 - Bb4 - A4 - G4 - F4 - - - C4 C5 C5 - - - C4 C5 C5 - - - C4 C5 Bb4 - A4 - G4 - F4 - - - - - C5 - - - - - - - - - - - - - - - - - - - - - C#5 - E5 D5 C5 Bb4 A4 G4 F4 - F4 - - -',
        bass: 'F2 - C2 - C2 - C2 - G2 - G2 - C2 - G2 - G2 - F2 - C2 - C2 - F2 - C2 - C2 - C2 - G2 - G2 - C2 - G2 - G2 - F2 - C2 - C2 - F2 - C2 - C2 - C2 - G2 - G2 - C2 - G2 - G2 - F2 - C2 - C2 - F2 - C2 - C2 - C2 - G2 - G2 - C2 - G2 - G2 - F2 - C2 - C2 - G2 - D2 - D2 - C2 - G2 - G2 - A2 - E2 - E2 - D2 - A2 - A2 - C2 - G2 - G2 - F2 - C2 - C2 - C2 - G2 - G2 - F2 - C2 - C2 - C2 - G2 - G2 - F2 - C2 - C2 - C2 - G2 - G2 - C2 - G2 - G2 - C2 - G2 - G2 - F2 - C2 - C2 - C2 - G2 - G2 - F2 - C2 - C2 - G2 - G2 - G2 - F2 - C2 - C2 -',
        harm: 'A4 - - - - - E4 - - - - - E4 - - - - - A4 - - - - - A4 - - - - - E4 - - - - - E4 - - - - - A4 - - - - - A4 - - - - - E4 - - - - - E4 - - - - - A4 - - - - - A4 - - - - - E4 - - - - - E4 - - - - - A4 - - - - - B4 - - - - - E4 - - - - - C#4 - - - - - F4 - - - - - E4 - - - - - A4 - - - - - E4 - - - - - A4 - - - - - E4 - - - - - A4 - - - - - E4 - - - - - E4 - - - - - E4 - - - - - A4 - - - - - E4 - - - - - A4 - - - - - Bb4 - E4 - - - A4 - - - - -' },
      drums: 'k . h . h .' },
    { id: 'lucia', title: "Santa Lucia (Cottrau)", bpm: 190, beat: 6, loops: 2, trem: false, parts: 'A',   // public domain: melody as written (abcnotation.com)
      A: {
        lead: 'D5 - D5 - - G5 G5 F#5 F#5 - - - C5 - C5 - - E5 E5 - D5 - - - B4 - E5 - D5 - D5 C#5 C5 - - - C5 - B4 - A4 - E5 - D5 - - - B5 - A5 - G5 - F#5 E5 A5 - - - A5 - G5 - E5 - C#5 D5 G5 - - - B5 G5 G5 D5 D5 B4 C5 A5 A5 - - - A5 - E5 - - F#5 A5 - G5 - - - B5 - A5 - G5 - F#5 E5 A5 - - - A5 - G5 - E5 - C#5 D5 G5 - - - B5 G5 G5 D5 D5 B4 C5 A5 A5 - - - A5 - B5 - - A5 A5 - G5 - - -',
        bass: 'G2 - D2 - D2 - D2 - A2 - A2 - C2 - G2 - G2 - G2 - D2 - D2 - E2 - B2 - B2 - A2 - E2 - E2 - D2 - A2 - A2 - G2 - D2 - D2 - G2 - D2 - D2 - A2 - E2 - E2 - C2 - G2 - G2 - G2 - D2 - D2 - G2 - D2 - D2 - A2 - E2 - E2 - D2 - A2 - A2 - D2 - D2 - D2 - G2 - D2 - D2 - A2 - E2 - E2 - C2 - G2 - G2 - G2 - D2 - D2 - G2 - D2 - D2 - A2 - E2 - E2 - D2 - A2 - A2 - D2 - D2 - D2 -',
        harm: 'B4 - - - - - F#4 - - - - - E4 - - - - - B4 - - - - - Ab4 - - - - - C4 - - - - - F#4 - - - - - B4 - - - - - B4 - - - - - C4 - - - - - E4 - - - - - B4 - - - - - B4 - - - - - C4 - - - - - F#4 - - - - - F#4 - B4 - - - B4 - - - - - C4 - - - - - E4 - - - - - B4 - - - - - B4 - - - - - C4 - - - - - F#4 - - - - - F#4 - B4 - - -' },
      drums: 'k . h . h .' },
    { id: 'solemio', title: "'O sole mio (Di Capua)", bpm: 150, beat: 8, loops: 1, trem: false, parts: 'A',   // public domain: melody as written (abcnotation.com)
      A: {
        lead: '. . G5 - F5 - E5 - D5 - - - C5 - - - C5 - D5 - E5 - C5 - B4 - - - A4 - - - . . B4 - C5 - D5 - B4 - A4 - A4 - - - - - B4 - C5 - D5 - A4 - G4 - G4 - - - . . G5 - F5 - E5 - D5 - - - C5 - - - C5 - D5 - E5 - C5 - B4 - - - A4 - - - . . F5 - E5 - D5 - G5 - E5 - D5 - C5 - D5 - - - - - E5 - D5 - - - C5 - - - . . C6 - C6 - B5 - B5 - G5 - G5 - - - . . B5 - B5 - A5 - F5 - - - - - - - . . B5 - B5 - A5 - F5 - - - F5 - - - . . D5 - E5 - F5 - G5 - - - - - - - . . . . . . G5 - Ab5 - - - Ab5 - - - . . F5 - C6 - - Ab5 G5 - - - G5 - - - . . E5 - D5 - C5 - G5 - - - - - - - . . E5 - D5 - - B4 C5 - - - - - - -',
        bass: 'C2 - G2 - G2 - G2 - C2 - G2 - G2 - G2 - C2 - G2 - G2 - G2 - D2 - A2 - A2 - A2 - D2 - A2 - A2 - A2 - G2 - D2 - D2 - D2 - G2 - D2 - D2 - D2 - C2 - G2 - G2 - G2 - C2 - G2 - G2 - G2 - C2 - G2 - G2 - G2 - C2 - G2 - G2 - G2 - D2 - A2 - A2 - A2 - D2 - A2 - A2 - A2 - C2 - G2 - G2 - G2 - G2 - D2 - D2 - D2 - C2 - G2 - G2 - G2 - C2 - G2 - G2 - G2 - C2 - G2 - G2 - G2 - C2 - G2 - G2 - G2 - D2 - A2 - A2 - A2 - D2 - A2 - A2 - A2 - D2 - A2 - A2 - A2 - G2 - D2 - D2 - D2 - C2 - G2 - G2 - G2 - C2 - G2 - G2 - G2 - F2 - C2 - C2 - C2 - F2 - C2 - C2 - C2 - C2 - G2 - G2 - G2 - C2 - G2 - G2 - G2 - G2 - D2 - D2 - D2 - G2 - D2 - D2 - D2 - C2 - G2 - G2 - G2 -',
        harm: 'E4 - - - - - - - E4 - - - - - - - E4 - - - - - - - F4 - - - - - - - F4 - - - - - - - B4 - - - - - - - B4 - - - - - - - E4 - - - - - - - E4 - - - - - - - E4 - - - - - - - E4 - - - - - - - F4 - - - - - - - F4 - - - - - - - E4 - - - - - - - B4 - - - - - - - E4 - - - - - - - E4 - - - - - - - E4 - - - - - - - E4 - - - - - - - F4 - - - - - - - F4 - - - - - - - F4 - - - - - - - B4 - - - - - - - E4 - - - - - - - E4 - - - - - - - Ab4 - - - - - - - Ab4 - - - - - - - E4 - - - - - - - E4 - - - - - - - B4 - - - - - - - B4 - - - - - - - E4 - - - - - - -' },
      drums: 'k . h . s . h .' },
    { id: 'tarnap', title: "Tarantella napoletana (trad.)", bpm: 390, beat: 6, loops: 1, trem: false, parts: 'A',   // public domain: melody as written (abcnotation.com)
      A: {
        lead: 'A5 - A5 E5 - E5 A5 - A5 E5 - - E5 - E5 F5 - - F5 G5 F5 F5 - E5 E5 F5 E5 E5 - D5 D5 E5 D5 D5 - C5 C5 D5 C5 B4 - B4 C5 - B4 A4 - . A4 - B4 C5 B4 C5 D5 C5 B4 C5 B4 C5 D5 C5 B4 C5 B4 A4 Ab4 A4 B4 A4 - . A4 - B4 C5 B4 C5 D5 C5 D5 E5 D5 E5 F5 E5 D5 C5 B4 A4 Ab4 A4 B4 A4 - . A5 - A5 E5 - E5 A5 - A5 E5 - - E5 - E5 F5 - - F5 G5 F5 F5 - E5 E5 F5 E5 E5 - D5 D5 E5 D5 D5 - C5 C5 D5 C5 B4 - B4 C5 - B4 A4 - . G4 A4 B4 C5 B4 C5 E5 C5 E5 G5 - - G5 A5 G5 G5 - F5 F5 G5 F5 F5 - E5 G4 A4 B4 C5 B4 C5 E5 C5 E5 G5 - - G5 F#5 G5 B5 A5 G5 F5 E5 D5 C5 - . A5 - A5 E5 - E5 A5 - A5 E5 - - E5 - E5 F5 - - F5 G5 F5 F5 - E5 E5 F5 E5 E5 - D5 D5 E5 D5 D5 - C5 C5 D5 C5 B4 - B4 C5 - B4 A4 - . E5 - F5 G5 - G5 A5 - G5 F5 - E5 D5 - E5 F5 - F5 G5 - F5 E5 - D5 C5 - E5 G5 - G5 A5 - G5 F5 - E5 D5 - E5 F5 - F5 E5 - D5 C5 - .',
        bass: '. . . A2 - - E2 - - A2 - - E2 - - D2 - - A2 - - A2 - - E2 - - E2 - - B2 - - A2 - - E2 - - E2 - - B2 - - A2 - - E2 - - A2 - - A2 - - A2 - - A2 - - A2 - - B2 - - A2 - - E2 - - A2 - - A2 - - A2 - - A2 - - A2 - - B2 - - A2 - - E2 - - A2 - - E2 - - A2 - - E2 - - D2 - - A2 - - A2 - - E2 - - E2 - - B2 - - A2 - - E2 - - E2 - - B2 - - A2 - - D2 - - C2 - - G2 - - C2 - - G2 - - G2 - - D2 - - C2 - - D2 - - C2 - - G2 - - C2 - - G2 - - G2 - - D2 - - C2 - - G2 - - A2 - - E2 - - A2 - - E2 - - D2 - - A2 - - A2 - - E2 - - E2 - - B2 - - A2 - - E2 - - E2 - - B2 - - A2 - - E2 - - C2 - - G2 - - G2 - - D2 - - G2 - - D2 - - C2 - - G2 - - A2 - - E2 - - D2 - - A2 - - G2 - - D2 - - C2 - -',
        harm: '. . . C4 - - - - - C4 - - - - - F4 - - - - - C4 - - - - - Ab4 - - - - - C4 - - - - - Ab4 - - - - - C4 - - - - - C4 - - F4 - - C4 - - F4 - - C4 - - Ab4 - - C4 - - - - - C4 - - F4 - - C4 - - F4 - - C4 - - Ab4 - - C4 - - - - - C4 - - - - - C4 - - - - - F4 - - - - - C4 - - - - - Ab4 - - - - - C4 - - - - - Ab4 - - - - - C4 - - B4 - - E4 - - - - - E4 - - - - - B4 - - - - - E4 - - B4 - - E4 - - - - - E4 - - - - - B4 - - - - - E4 - - - - - C4 - - - - - C4 - - - - - F4 - - - - - C4 - - - - - Ab4 - - - - - C4 - - - - - Ab4 - - - - - C4 - - - - - E4 - - - - - B4 - - - - - B4 - - - - - E4 - - - - - C#4 - - - - - F4 - - - - - B4 - - - - - E4 - -' },
      drums: 'k . h s . h' },
  ];

  const PREF = 'pm-music';               // per-browser setting, kept apart from the game save
  let lastIdx = Math.floor(Math.random() * SONGS.length) - 1, ctx = null, master = null, bus = null, wobble = null, voices = [], timer = null, current = null, armed = false;   // the first tune is random (then the fixed order carries on from it)
  const VOL = 'pm-music-vol', LEVELS = [.25, .5, 1, 1.6, 2.3];   // 1 = low ... 5 = max; 3 (the middle) is the default
  const getVol = () => { try { const v = +localStorage.getItem(VOL); return v >= 1 && v <= 5 ? v : 3 } catch (_) { return 3 } };
  const gainFor = v => .16 * LEVELS[v - 1];
  const prefOn = () => { try { return localStorage.getItem(PREF) !== 'off' } catch (_) { return true } };
  const setPref = on => { try { localStorage.setItem(PREF, on ? 'on' : 'off') } catch (_) {} };

  const NOTE = { C: 0, 'C#': 1, Db: 1, D: 2, 'D#': 3, Eb: 3, E: 4, F: 5, 'F#': 6, Gb: 6, G: 7, 'G#': 8, Ab: 8, A: 9, 'A#': 10, Bb: 10, B: 11 };
  const freq = n => { const m = /^([A-G][#b]?)(\d)$/.exec(n); if (!m) return 0; return 440 * Math.pow(2, (NOTE[m[1]] + (+m[2] + 1) * 12 - 69) / 12) };

  // turn "A4 - - B4 . ." into [{f, start, len}] in steps
  function parse(str) {
    const toks = str.replace(/\|/g, ' ').trim().split(/\s+/), out = [];
    toks.forEach((tk, i) => {
      if (tk === '-') { if (out.length && out[out.length - 1].start + out[out.length - 1].len === i) out[out.length - 1].len++; return }
      if (tk === '.') return;
      out.push({ f: freq(tk), start: i, len: 1 });
    });
    return { notes: out, steps: toks.length };
  }

  function pulseWave(duty) {             // square wave with a narrow duty cycle, the classic 8-bit lead
    const n = 32, re = new Float32Array(n), im = new Float32Array(n);
    for (let k = 1; k < n; k++) im[k] = 2 / (k * Math.PI) * Math.sin(k * Math.PI * duty);
    return ctx.createPeriodicWave(re, im);
  }

  function init() {
    if (ctx) return true;
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return false;
    ctx = new AC();
    const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 3200; lp.Q.value = .4;   // lo-fi: soften the top
    master = ctx.createGain(); master.gain.value = gainFor(getVol());
    // a limiter at the end: stacked voices at high volume used to clip (crackles)
    const lim = ctx.createDynamicsCompressor(); lim.threshold.value = -10; lim.knee.value = 6; lim.ratio.value = 12; lim.attack.value = .003; lim.release.value = .2;
    master.connect(lp); lp.connect(lim); lim.connect(ctx.destination);
    wobble = ctx.createOscillator(); wobble.frequency.value = .35;                                     // slow tape wobble
    const depth = ctx.createGain(); depth.gain.value = 6; wobble.connect(depth); wobble.start();
    wobble.depth = depth;
    return true;
  }

  function tone(type, f, t0, dur, vol, opts = {}) {
    const o = ctx.createOscillator(), g = ctx.createGain();
    if (type === 'pulse') o.setPeriodicWave(pulseWave(opts.duty || .25)); else o.type = type;
    o.frequency.value = f;
    if (opts.wobble) wobble.depth.connect(o.detune);
    // soft edges in time order, even for very short notes (tremolo picks): out-of-order ramps were the pops
    const att = Math.min(.012, dur / 4), rel = Math.min(.04, dur / 3);
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(vol, t0 + att);
    g.gain.setValueAtTime(vol, t0 + dur - rel);
    g.gain.linearRampToValueAtTime(0, t0 + dur);
    o.connect(g); g.connect(bus); o.start(t0); o.stop(t0 + dur + .02);
    voices.push(o);
  }

  let noiseBuf = null;
  function drum(kind, t0) {
    if (kind === 'k') {                                  // kick: sine sweeping down
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.frequency.setValueAtTime(150, t0); o.frequency.exponentialRampToValueAtTime(45, t0 + .12);
      g.gain.setValueAtTime(0, t0); g.gain.linearRampToValueAtTime(.55, t0 + .004); g.gain.exponentialRampToValueAtTime(.001, t0 + .15);
      o.connect(g); g.connect(bus); o.start(t0); o.stop(t0 + .16); voices.push(o); return;
    }
    if (!noiseBuf) { noiseBuf = ctx.createBuffer(1, ctx.sampleRate * .2, ctx.sampleRate); const d = noiseBuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1 }
    const s = ctx.createBufferSource(), g = ctx.createGain(), hp = ctx.createBiquadFilter();
    s.buffer = noiseBuf; hp.type = 'highpass'; hp.frequency.value = kind === 'h' ? 7000 : 1800;
    const len = kind === 'h' ? .03 : .11, vol = kind === 'h' ? .08 : .22;
    g.gain.setValueAtTime(0, t0); g.gain.linearRampToValueAtTime(vol, t0 + .003); g.gain.exponentialRampToValueAtTime(.001, t0 + len);
    s.connect(hp); hp.connect(g); g.connect(bus); s.start(t0); s.stop(t0 + len + .01); voices.push(s);
  }

  // schedule a whole song from now; returns its length in seconds
  function schedule(song) {
    const step = 60 / song.bpm;
    let t = ctx.currentTime + .15;
    const start = t;
    for (let loop = 0; loop < song.loops; loop++) {
      for (const p of song.parts) {
        const part = song[p];
        const lead = parse(part.lead), bass = parse(part.bass), harm = parse(part.harm);
        for (const n of lead.notes) {
          const dur = n.len * step;
          if (song.trem && n.len >= 2) {                // mandolin tremolo: the long notes are picked again and again
            const pick = step / 2;
            for (let k = 0; k < dur - .01; k += pick) tone('pulse', n.f, t + n.start * step + k, Math.min(pick, dur - k) * .95, .22 - (k / dur) * .06, { wobble: true });
          } else tone('pulse', n.f, t + n.start * step, dur * .92, .24, { wobble: true });
        }
        for (const n of bass.notes) tone('triangle', n.f, t + n.start * step, n.len * step * .95, .38);
        for (const n of harm.notes) tone('pulse', n.f, t + n.start * step, n.len * step * .9, .07, { duty: .5 });
        const dr = song.drums.split(/\s+/);
        for (let i = 0; i < lead.steps; i++) { const d = dr[i % dr.length]; if (d !== '.') drum(d, t + i * step) }
        t += lead.steps * step;
      }
    }
    return t - start;
  }

  // each song plays through its own bus: cutting the bus silences every note still scheduled, even if the
  // audio clock was suspended (phones) and the wall-clock timer ran ahead of it
  function stopAll() { clearTimeout(timer); timer = null; voices.forEach(v => { try { v.stop() } catch (_) {} }); voices = [];
    if (bus) { try { bus.disconnect() } catch (_) {} bus = null } current = null }

  function play(id) {
    if (!init()) return;
    if (ctx.state === 'suspended') ctx.resume();
    stopAll();
    // fixed order: each new tune is the one after the last played (it starts with the first)
    const song = SONGS.find(s => s.id === id) || SONGS[(lastIdx + 1) % SONGS.length];
    lastIdx = SONGS.indexOf(song);
    current = song;
    bus = ctx.createGain(); bus.connect(master);
    const endAt = ctx.currentTime + schedule(song);
    // after the tune (by the audio clock, which stops while the phone suspends sound), a quiet break of 60–120 s, then another one
    const done = () => { if (ctx.currentTime < endAt) { timer = setTimeout(done, 2000); return }
      stopAll(); timer = setTimeout(() => { if (prefOn() && !current) play() }, (60 + Math.random() * 60) * 1000) };
    timer = setTimeout(done, (endAt - ctx.currentTime) * 1000 + 300);
    document.dispatchEvent(new CustomEvent('pm-music', { detail: song.title }));
  }

  // browsers only allow sound after the player touches the page: start on the first tap or key
  function arm() {
    if (armed) return; armed = true;
    const go = () => { window.removeEventListener('pointerdown', go); window.removeEventListener('keydown', go); if (prefOn()) setTimeout(() => { if (!current) play() }, 1500) };
    window.addEventListener('pointerdown', go); window.addEventListener('keydown', go);
  }

  return {
    songs: SONGS, arm, play, stop: stopAll,
    isOn: prefOn,
    volume: getVol,
    setVolume(v) { v = Math.max(1, Math.min(5, Math.round(v))); try { localStorage.setItem(VOL, v) } catch (_) {}
      if (master) master.gain.setTargetAtTime(gainFor(v), ctx.currentTime, .05); return v },
    playing: () => current && current.title,
    toggle() { const on = !prefOn(); setPref(on); if (on) play(); else stopAll(); return on },
    next() { setPref(true); play() },
  };
})();
