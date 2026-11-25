/* Pizza Magna — 8-bit / lo-fi Italian music, synthesised with Web Audio (no audio files).
   Four voices like an old console: square lead (25% duty), triangle bass, soft square harmony, noise drums,
   through a gentle low-pass filter with a slow "tape" wobble for the lo-fi feel.
   The tunes are original compositions in the style of Neapolitan classics, the tarantella and Verdi's "La donna è mobile",
   plus a swaying 1950s crooner tune and a slow romantic ballad.
   The last four are public-domain classics, melody as written: converted from ABC by tools/abc2music.py.
   Notation: one token per step (an eighth note); "-" holds the previous note, "." is silence.
   Drums: k = kick, s = snare, h = hat, . = nothing.
   The lo-fi tunes (lofi: true, original) add an arpeggio line (arp) and hold chords in harm ("F3+A3+C4" plays them together);
   they play with a softer lead (tone: round, bell or flute), a soft pad, quieter drums and a warmer filter, a part may bring its
   own drums, and they alternate with the Italian tunes (ORDER). */
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
    // calm tunes: slow and quiet, in the same order as the others (see ORDER)
    { id: 'venezia', title: 'Notte a Venezia', calm: true, bpm: 110, beat: 6, loops: 2, trem: true, parts: 'A',   // a gentle barcarolle
      A: {
        lead: 'E5 - - D5 C5 - | B4 - - A4 - - | C5 - - B4 A4 - | G#4 - - - - - | A4 - - B4 C5 - | D5 - - E5 - - | C5 - B4 - A4 - | A4 - - - . .',
        bass: 'A2 - E3 - A3 - | E2 - B2 - E3 - | A2 - E3 - A3 - | E2 - B2 - E3 - | F2 - C3 - F3 - | D2 - A2 - D3 - | E2 - B2 - E3 - | A2 - - - . .',
        harm: 'C4 - - - - - | G#3 - - - - - | A3 - - - - - | B3 - - - - - | A3 - - - - - | F3 - - - - - | G#3 - - - - - | C4 - - - . .' },
      drums: 'k . . . . .' },
    { id: 'ninna', title: 'Ninna Nanna del Forno', calm: true, bpm: 100, beat: 6, loops: 2, trem: false, parts: 'A',   // a lullaby by the oven
      A: {
        lead: 'C5 - A4 - F4 - | G4 - A4 - Bb4 - | A4 - - - G4 - | F4 - - - - - | C5 - D5 - C5 - | Bb4 - A4 - G4 - | A4 - G4 - E4 - | F4 - - - . .',
        bass: 'F2 - - - C3 - | C2 - - - G2 - | F2 - - - C3 - | F2 - - - C3 - | A2 - - - F2 - | Bb1 - - - F2 - | C2 - - - G2 - | F2 - - - . .',
        harm: 'A3 - - - - - | E4 - - - - - | C4 - - - - - | A3 - - - - - | F4 - - - - - | D4 - - - - - | Bb3 - - - - - | A3 - - - . .' },
      drums: '. . . . . .' },
    { id: 'toscana', title: 'Tramonto in Toscana', calm: true, bpm: 116, beat: 8, loops: 2, trem: false, parts: 'A',   // sunset over the hills
      A: {
        lead: 'D5 - - - B4 - G4 - | A4 - - - - - B4 - | C5 - - - A4 - F#4 - | G4 - - - - - . . | E5 - - - D5 - C5 - | B4 - - - A4 - G4 - | A4 - - - F#4 - A4 - | G4 - - - - - . .',
        bass: 'G2 - - - D3 - - - | D2 - - - A2 - - - | C2 - - - G2 - - - | G2 - - - D3 - - - | C2 - - - G2 - - - | G2 - - - D3 - - - | D2 - - - A2 - - - | G2 - - - - - . .',
        harm: 'B3 - - - - - - - | F#4 - - - - - - - | E4 - - - - - - - | D4 - - - - - - - | G4 - - - - - - - | D4 - - - - - - - | C4 - - - - - - - | B3 - - - - - . .' },
      drums: 'k . . . h . . .' },
    // lo-fi tunes, each with its own idea: soft jazzy chords and an arpeggio (from the reactions clip), a rainy 6/8 with raindrop notes,
    // a swing with a walking bass, a bossa nova, a boom-bap with a hook riff, a ballad over a held bass.
    // tone: the lead's sound, 'round' (a 50% pulse), 'bell' (a thin, short pulse) or 'flute' (a triangle); a part's own drums replace the tune's
    { id: 'margherita', title: 'Lo-fi Margherita', lofi: true, bpm: 152, beat: 8, loops: 4, trem: false, parts: 'A',
      A: {
        lead: '. . C5 - . A4 - - | . . . G4 - - . . | . A4 - . C5 - D5 - | . . . B4 - - - . | . . A4 - . F4 - - | . . G4 - E4 - - -',
        bass: 'F2 - - - C3 - - - | E2 - - - B2 - - - | D2 - - - A2 - - - | C2 - - - G2 - - - | Bb1 - - - F2 - - - | C2 - - - G2 - - -',
        harm: 'A3+C4+E4+F4 - - - - - - - | G3+B3+D4+E4 - - - - - - - | F3+A3+C4+D4 - - - - - - - | E3+G3+B3+C4 - - - - - - - | D3+F3+A3+Bb3 - - - - - - - | E3+G3+B3+C4 - - - - - - -',
        arp: 'A4 C5 E5 F5 E5 C5 E5 C5 | G4 B4 D5 E5 D5 B4 D5 B4 | F4 A4 C5 D5 C5 A4 C5 A4 | E4 G4 B4 C5 B4 G4 B4 G4 | D4 F4 A4 Bb4 A4 F4 A4 F4 | E4 G4 B4 C5 B4 G4 B4 G4' },
      drums: 'k h s k . h s h' },
    { id: 'pioggia', title: 'Pioggia su Napoli', lofi: true, tone: 'flute', bpm: 84, beat: 6, loops: 1, trem: false, parts: 'AB',
      A: {
        lead: 'F5 - - Eb5 - - | C#5 - - - - - | C#5 - - Bb4 - - | C5 - - - - - | F5 - - Eb5 - - | Eb5 - - C#5 - - | Bb4 - - - - - | C5 - - Ab4 - -',
        bass: 'C#2 - - - - - | Bb2 - - - - - | F#2 - - - - - | Ab2 - - - - - | F2 - - - - - | Bb2 - - - - - | Eb2 - - - - - | Ab2 - - - - -',
        harm: 'C#5 - - C5 - - | Bb4 - - - - - | Bb4 - - F#4 - - | Ab4 - - - - - | C#5 - - C5 - - | C5 - - Bb4 - - | F#4 - - - - - | Ab4 - - F4 - -',
        arp: 'Ab3 - C#4 - C5 - | Bb3 - C#4 - C5 - | F#3 - Bb3 - F4 - | Ab3 - C4 - F4 - | F3 - Ab3 - Eb4 - | F3 - Bb3 - F4 - | F#3 - Bb3 - F4 - | Ab3 - C4 - F#4 -',
        drums: '. . . . . .' },
      B: {
        lead: 'F5 - - - - - | F5 - - C#5 - - | Eb5 - - C#5 - - | C5 - - - - - | C#5 - - C5 - - | Bb4 - - - - - | Ab4 - - C5 - - | C#5 - - - - -',
        bass: 'F#2 - - - - - | F2 - - - - - | Eb2 - - - - - | C#2 - - - - - | Bb2 - - - - - | F#2 - - - - - | Ab2 - - - - - | C#2 - - - - -',
        harm: 'C#5 - - - - - | C#5 - - Bb4 - - | C5 - - Bb4 - - | Ab4 - - - - - | Bb4 - - Ab4 - - | F#4 - - - - - | F4 - - Ab4 - - | Bb4 - - - - -',
        arp: 'F#3 - Bb3 - F4 - | F3 - Ab3 - Eb4 - | Eb3 - F#3 - C#4 - | F3 - Ab3 - C#4 - | Bb3 - C#4 - C5 - | F#3 - Bb3 - F4 - | Ab3 - C#4 - Ab4 - | Ab3 - C#4 - Ab4 -',
        drums: '. . . . . .' },
      drums: '. . . . . .' },
    { id: 'mezzanotte', title: 'Forno a Mezzanotte', lofi: true, tone: 'round', bpm: 132, beat: 8, loops: 1, trem: false, parts: 'AB',
      A: {
        lead: '. . F5 - E5 - - - | . D5 - - . B4 - - | C5 - - - - - . . | . . . C#5 - E5 - - | . . F5 - D5 - C5 - | . B4 - - D5 - - - | E5 - - - - - - - | . . . . . . . .',
        bass: 'D2 - - - A2 - - Ab2 | G2 - - - D3 - - C#2 | C2 - - - G2 - - Bb2 | A2 - - - E3 - - Eb2 | D2 - - - A2 - - Ab2 | G2 - - - D3 - - C#2 | C2 - - - G2 - - F2 | C2 - - - G2 - - Eb2',
        harm: 'A3+C4+E4+F4 - - . . A3+C4+E4+F4 - - | F3+B3+D4+F4 - - . . F3+B3+D4+F4 - - | G3+B3+C4+E4 - - . . G3+B3+C4+E4 - - | G3+C#4+E4+G4 - - . . G3+C#4+E4+G4 - - | A3+C4+E4+F4 - - . . A3+C4+E4+F4 - - | F3+B3+D4+F4 - - . . F3+B3+D4+F4 - - | G3+B3+C4+E4 - - . . G3+B3+C4+E4 - - | G3+A3+C4+E4 - - . . G3+A3+C4+E4 - -' },
      B: {
        lead: 'A5 - - - . F5 - - | G5 - - - F5 - D5 - | E5 - - - - - - - | . . C#5 - - A4 - - | D5 - - . F5 - - - | G5 - F5 - D5 - - - | C5 - - - - - . . | . . . . . . . .',
        bass: 'D2 - - - A2 - - Ab2 | G2 - - - D3 - - C#2 | C2 - - - G2 - - Bb2 | A2 - - - E3 - - Eb2 | D2 - - - A2 - - Ab2 | G2 - - - D3 - - C#2 | C2 - - - G2 - - F2 | C2 - - - G2 - - Eb2',
        harm: 'A3+C4+E4+F4 - - . . A3+C4+E4+F4 - - | F3+B3+D4+F4 - - . . F3+B3+D4+F4 - - | G3+B3+C4+E4 - - . . G3+B3+C4+E4 - - | G3+C#4+E4+G4 - - . . G3+C#4+E4+G4 - - | A3+C4+E4+F4 - - . . A3+C4+E4+F4 - - | F3+B3+D4+F4 - - . . F3+B3+D4+F4 - - | G3+B3+C4+E4 - - . . G3+B3+C4+E4 - - | G3+A3+C4+E4 - - . . G3+A3+C4+E4 - -' },
      drums: 'k . . h s . . h' },
    { id: 'vespa', title: 'Vespa Lenta', lofi: true, tone: 'flute', bpm: 240, beat: 8, loops: 4, trem: false, parts: 'A',
      A: {
        lead: 'F#5 - - - - - E5 - | D5 - - - C#5 - - - | B4 - - - - - D5 - | C#5 - - - - - - - | A5 - - - F#5 - E5 - | F#5 - - - C5 - - - | B4 - - - D5 - F#5 - | E5 - - - - - Bb4 -',
        bass: 'D2 - - A2 A2 - - D2 | B1 - - F#2 F#2 - - B1 | E2 - - B2 B2 - - E2 | A2 - - E3 E3 - - A2 | D2 - - A2 A2 - - D2 | D2 - - A2 A2 - - D2 | G2 - - D3 D3 - - G2 | G2 - - D3 D3 - - G2',
        harm: 'F#3+A3+C#4+D4 - . F#3+A3+C#4+D4 . F#3+A3+C#4+D4 - . | . . F#3+A3+B3+D4 - F#3+A3+B3+D4 . F#3+A3+B3+D4 - | G3+B3+D4+E4 - . G3+B3+D4+E4 . G3+B3+D4+E4 - . | . . G3+A3+C#4+E4 - G3+A3+C#4+E4 . G3+A3+C#4+E4 - | F#3+A3+C#4+D4 - . F#3+A3+C#4+D4 . F#3+A3+C#4+D4 - . | . . F#3+A3+C4+D4 - F#3+A3+C4+D4 . F#3+A3+C4+D4 - | F#3+G3+B3+D4 - . F#3+G3+B3+D4 . F#3+G3+B3+D4 - . | . . G3+Bb3+D4+E4 - G3+Bb3+D4+E4 . G3+Bb3+D4+E4 -' },
      drums: 'k h h s h h s h k h s h h s h h' },
    { id: 'caffe', title: 'Caffè Sospeso', lofi: true, tone: 'round', bpm: 172, beat: 8, loops: 2, trem: false, parts: 'AB',
      A: {
        lead: '. . . . . . . . | . . . . . . . . | . . . . . . . . | . . . . . . . . | . . . . . . . . | . . . . . . . . | . . . . . . . . | . . . . . . . .',
        bass: 'F2 - . F2 . F3 Eb3 - | C#2 - . C#2 . C#3 B2 - | Bb1 - . Bb1 . Bb2 Ab2 - | C2 - . C2 . C3 Bb2 - | F2 - . F2 . F3 Eb3 - | C#2 - . C#2 . C#3 B2 - | Bb1 - . Bb1 . Bb2 Ab2 - | C2 - . C2 . C3 Bb2 -',
        harm: '. . . . . . . . | . . . . . . . . | . . . . . . . . | . . . . . . . . | . . . . . . . . | . . . . . . . . | . . . . . . . . | . . . . . . . .',
        arp: 'G5 . Eb5 C5 - . Eb5 . | F5 . C#5 C5 - . C#5 . | F5 . C#5 Bb4 - . C#5 . | E5 . C5 Bb4 - . C5 . | G5 . Eb5 C5 - . Eb5 . | F5 . C#5 C5 - . C#5 . | F5 . C#5 Bb4 - . C#5 . | E5 . C5 Bb4 - . C5 .' },
      B: {
        lead: 'Ab5 - G5 F5 - - . . | . . C5 Eb5 F5 - - - | C#5 - F5 - Ab5 - - . | G5 - - - - - . . | C6 - Bb5 Ab5 - - . . | . F5 - Ab5 - C6 - - | Bb5 - Ab5 - F5 - - - | E5 - G5 - C5 - - -',
        bass: 'F2 - . F2 . F3 Eb3 - | C#2 - . C#2 . C#3 B2 - | Bb1 - . Bb1 . Bb2 Ab2 - | C2 - . C2 . C3 Bb2 - | F2 - . F2 . F3 Eb3 - | C#2 - . C#2 . C#3 B2 - | Bb1 - . Bb1 . Bb2 Ab2 - | C2 - . C2 . C3 Bb2 -',
        harm: 'Ab3+C4+Eb4+G4 - - - - - - - | Ab3+C4+C#4+F4 - - - - - - - | Ab3+Bb3+C#4+F4 - - - - - - - | G3+Bb3+C4+E4 - - - - - - - | Ab3+C4+Eb4+G4 - - - - - - - | Ab3+C4+C#4+F4 - - - - - - - | Ab3+Bb3+C#4+F4 - - - - - - - | G3+Bb3+C4+E4 - - - - - - -',
        arp: 'G5 . Eb5 C5 - . Eb5 . | F5 . C#5 C5 - . C#5 . | F5 . C#5 Bb4 - . C#5 . | E5 . C5 Bb4 - . C5 . | G5 . Eb5 C5 - . Eb5 . | F5 . C#5 C5 - . C#5 . | F5 . C#5 Bb4 - . C#5 . | E5 . C5 Bb4 - . C5 .' },
      drums: 'k . h . s . h k . k h . s . h .' },
    { id: 'terrazza', title: 'Terrazza al Tramonto', lofi: true, tone: 'flute', bpm: 120, beat: 8, loops: 1, trem: false, parts: 'AB',
      A: {
        lead: 'E5 - - - - - D5 - | C5 - - - F5 - - - | D5 - - - - - C5 - | B4 - - - - - - - | G5 - - - E5 - - - | A5 - - - - - G5 - | F5 - - - D5 - - - | D5 - - - - - - -',
        bass: 'C2 - - - - - - - | C2 - - - - - - - | C2 - - - - - - - | C2 - - - - - - - | C2 - - - - - - - | C2 - - - - - - - | C2 - - - - - - - | C2 - - - - - - -',
        harm: 'G3+B3+C4+E4 - - - - - - - | F3+A3+C4+F4 - - - - - - - | F3+A3+C4+D4 - - - - - - - | G3+B3+D4+G4 - - - - - - - | G3+B3+C4+E4 - - - - - - - | F3+A3+C4+F4 - - - - - - - | F3+A3+C4+D4 - - - - - - - | G3+B3+D4+G4 - - - - - - -',
        drums: '. . . . . . . .' },
      B: {
        lead: 'E5 - - - G5 - - - | G5 - - - - - F5 - | E5 - - - C5 - - - | D5 - - - - - - - | A5 - - - G5 - E5 - | G5 - - - E5 - - - | F5 - - - E5 - D5 - | D5 - - - B4 - - -',
        bass: 'A2 - - - E3 - - - | E2 - - - B2 - - - | F2 - - - C3 - - - | G2 - - - D3 - - - | A2 - - - E3 - - - | E2 - - - B2 - - - | F2 - - - C3 - - - | G2 - - - D3 - - -',
        harm: 'G3+A3+C4+E4 - - - - - - - | G3+B3+D4+E4 - - - - - - - | F3+A3+C4+E4 - - - - - - - | F3+G3+B3+D4 - - - - - - - | G3+A3+C4+E4 - - - - - - - | G3+B3+D4+E4 - - - - - - - | F3+A3+C4+E4 - - - - - - - | F3+G3+B3+D4 - - - - - - -',
        arp: 'G4 - C5 - E5 - A4 - | G4 - D5 - E5 - B4 - | F4 - C5 - E5 - A4 - | F4 - B4 - D5 - G4 - | G4 - C5 - E5 - A4 - | G4 - D5 - E5 - B4 - | F4 - C5 - E5 - A4 - | F4 - B4 - D5 - G4 -' },
      drums: 'k . . . s . . .' },
  ];

  // play order: an Italian tune, then a lo-fi one, and so on, each kind shuffled (the lo-fi ones are shuffled again
  // when they run out, as there are fewer); once every Italian tune has played, a new shuffle (calm ones are not put in between)
  const ITALIAN = SONGS.filter(s => !s.lofi), LOFI = SONGS.filter(s => s.lofi);
  const shuffle = a => { a = [...a]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]] } return a };
  let ORDER = [];
  function deal() { let lo = []; ORDER = shuffle(ITALIAN).flatMap(s => { if (!LOFI.length) return [s]; if (!lo.length) lo = shuffle(LOFI); return [s, lo.pop()] }) }
  deal();
  const PREF = 'pm-music';               // per-browser setting, kept apart from the game save
  let lastIdx = -1, ctx = null, master = null, bus = null, wobble = null, voices = [], timer = null, current = null, armed = false;   // the order is shuffled, so it starts at the top
  const VOL = 'pm-music-vol', LEVELS = [.25, .5, 1, 1.6, 2.3];   // 1 = low ... 5 = max; 2 is the default
  const getVol = () => { try { const v = +localStorage.getItem(VOL); return v >= 1 && v <= 5 ? v : 2 } catch (_) { return 2 } };
  const gainFor = v => .16 * LEVELS[v - 1];
  const prefOn = () => { try { return localStorage.getItem(PREF) !== 'off' } catch (_) { return true } };
  const setPref = on => { try { localStorage.setItem(PREF, on ? 'on' : 'off') } catch (_) {} };

  const NOTE = { C: 0, 'C#': 1, Db: 1, D: 2, 'D#': 3, Eb: 3, E: 4, F: 5, 'F#': 6, Gb: 6, G: 7, 'G#': 8, Ab: 8, A: 9, 'A#': 10, Bb: 10, B: 11 };
  const freq = n => { const m = /^([A-G][#b]?)(\d)$/.exec(n); if (!m) return 0; return 440 * Math.pow(2, (NOTE[m[1]] + (+m[2] + 1) * 12 - 69) / 12) };

  // turn "A4 - - B4 . ." into [{f, start, len}] in steps; "F3+A3+C4" is a chord, its notes held together by "-"
  function parse(str) {
    const toks = str.replace(/\|/g, ' ').trim().split(/\s+/), out = [];
    let last = [];
    toks.forEach((tk, i) => {
      if (tk === '-') { for (const n of last) if (n.start + n.len === i) n.len++; return }
      if (tk === '.') { last = []; return }
      last = tk.split('+').map(x => ({ f: freq(x), start: i, len: 1 })); out.push(...last);
    });
    return { notes: out, steps: toks.length };
  }

  const waves = {};                      // one wave per duty cycle, built once: a new one per note made phones stutter (crackles)
  function pulseWave(duty) {             // square wave with a narrow duty cycle, the classic 8-bit lead
    if (waves[duty]) return waves[duty];
    const n = 32, re = new Float32Array(n), im = new Float32Array(n);
    for (let k = 1; k < n; k++) im[k] = 2 / (k * Math.PI) * Math.sin(k * Math.PI * duty);
    return (waves[duty] = ctx.createPeriodicWave(re, im));
  }

  function init() {
    if (ctx) return true;
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return false;
    ctx = new AC({ latencyHint: 'playback' });   // bigger audio buffers: phones that fall behind make pops
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

  function toneNow(type, f, t0, dur, vol, opts = {}) {
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
    o.onended = () => { o.done = true; try { g.disconnect() } catch (_) {} }; voices.push(o);
  }

  let noiseBuf = null;
  function drumNow(kind, t0, sc = 1) {   // sc: quieter drums for the lo-fi tunes
    if (kind === 'k') {                                  // kick: sine sweeping down
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.frequency.setValueAtTime(150, t0); o.frequency.exponentialRampToValueAtTime(45, t0 + .12);
      g.gain.setValueAtTime(0, t0); g.gain.linearRampToValueAtTime(.55 * sc, t0 + .004); g.gain.exponentialRampToValueAtTime(.001, t0 + .15);
      o.connect(g); g.connect(bus); o.start(t0); o.stop(t0 + .16); voices.push(o); return;
    }
    if (!noiseBuf) { noiseBuf = ctx.createBuffer(1, ctx.sampleRate * .2, ctx.sampleRate); const d = noiseBuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1 }
    const s = ctx.createBufferSource(), g = ctx.createGain(), hp = ctx.createBiquadFilter();
    s.buffer = noiseBuf; hp.type = 'highpass'; hp.frequency.value = kind === 'h' ? 7000 : 1800;
    const len = kind === 'h' ? .03 : .11, vol = (kind === 'h' ? .08 : .22) * sc;
    g.gain.setValueAtTime(0, t0); g.gain.linearRampToValueAtTime(vol, t0 + .003); g.gain.exponentialRampToValueAtTime(.001, t0 + len);
    s.connect(hp); hp.connect(g); g.connect(bus); s.start(t0); s.stop(t0 + len + .01); voices.push(s);
  }

  // schedule a whole song from now; returns its length in seconds
  // notes are created only a little ahead of time (see pump): creating a whole tune's notes at once,
  // thousands of oscillators, made phones fall behind, and that was heard as pops everywhere
  let queue = [], qi = 0, pumpT = null;
  function pump() {
    const until = ctx.currentTime + .5;
    while (qi < queue.length && queue[qi][0] < until) { const [t0, fn] = queue[qi++]; if (t0 > ctx.currentTime - .02) fn() }
    voices = voices.filter(v => !v.done);
    pumpT = qi < queue.length ? setTimeout(pump, 150) : null;
  }
  function schedule(song) {
    queue = []; qi = 0; clearTimeout(pumpT);
    const tone = (...a) => queue.push([a[2], () => toneNow(...a)]), drum = (k, t0) => queue.push([t0, () => drumNow(k, t0, song.lofi ? .45 : 1)]);
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
          } else if (song.tone === 'bell') tone('pulse', n.f, t + n.start * step, Math.min(dur * .9, step * 1.5), .13, { duty: .125, wobble: true });
          else if (song.tone === 'flute') tone('triangle', n.f, t + n.start * step, dur * .92, .22, { wobble: true });
          else if (song.lofi) tone('pulse', n.f, t + n.start * step, dur * .9, .15, { duty: .5, wobble: true });   // rounder and softer
          else tone('pulse', n.f, t + n.start * step, dur * .92, .24, { wobble: true });
        }
        for (const n of bass.notes) tone('triangle', n.f, t + n.start * step, n.len * step * .95, .38);
        if (song.lofi) for (const n of harm.notes) tone('triangle', n.f, t + n.start * step, n.len * step, .05);   // a soft pad
        else for (const n of harm.notes) tone('pulse', n.f, t + n.start * step, n.len * step * .9, .07, { duty: .5 });
        if (part.arp) for (const n of parse(part.arp).notes) tone('pulse', n.f, t + n.start * step, n.len * step * .9, .06, { duty: .5 });
        const dr = (part.drums || song.drums).split(/\s+/);
        for (let i = 0; i < lead.steps; i++) { const d = dr[i % dr.length]; if (d !== '.') drum(d, t + i * step) }
        t += lead.steps * step;
      }
    }
    queue.sort((a, b) => a[0] - b[0]); pump();
    return t - start;
  }

  // each song plays through its own bus: cutting the bus silences every note still scheduled, even if the
  // audio clock was suspended (phones) and the wall-clock timer ran ahead of it
  // fade the old tune out over 80 ms before cutting it: stopping notes mid-wave was a click
  function stopAll() { clearTimeout(timer); timer = null; clearTimeout(pumpT); pumpT = null; queue = []; qi = 0;
    const vs = voices, b = bus; voices = []; bus = null; current = null;
    if (!ctx) return;
    const now = ctx.currentTime;
    if (b) { b.gain.cancelScheduledValues(now); b.gain.setValueAtTime(b.gain.value, now); b.gain.linearRampToValueAtTime(0, now + .08) }
    vs.forEach(v => { try { v.stop(now + .1) } catch (_) {} });
    if (b) setTimeout(() => { try { b.disconnect() } catch (_) {} }, 200) }

  function play(id) {
    if (!init()) return;
    if (ctx.state === 'suspended') ctx.resume();
    stopAll();
    // each new tune is the next in the shuffled order; at the end, a new shuffle
    const asked = SONGS.find(s => s.id === id);
    if (!asked && lastIdx + 1 >= ORDER.length) { deal(); lastIdx = -1 }
    lastIdx = asked ? ORDER.indexOf(asked) : lastIdx + 1;
    const song = asked || ORDER[lastIdx];
    current = song;
    bus = ctx.createGain(); bus.gain.setValueAtTime(0, ctx.currentTime); bus.gain.linearRampToValueAtTime(song.calm ? .7 : 1, ctx.currentTime + .1); if (song.lofi) { const warm = ctx.createBiquadFilter(); warm.type = 'lowpass'; warm.frequency.value = 1500; warm.Q.value = .5; bus.connect(warm); warm.connect(master) } else bus.connect(master);   // calm tunes play a little quieter; lo-fi ones through a warmer filter
    const startAt = ctx.currentTime, endAt = startAt + schedule(song);
    // after the tune (by the audio clock, which stops while the phone suspends sound), a quiet break: a new tune starts every 3 minutes
    const done = () => { if (ctx.currentTime < endAt) { timer = setTimeout(done, 2000); return }
      stopAll(); timer = setTimeout(() => { if (prefOn() && !current) play() }, Math.max(2, 180 - (ctx.currentTime - startAt)) * 1000) };
    timer = setTimeout(done, (endAt - ctx.currentTime) * 1000 + 300);
    document.dispatchEvent(new CustomEvent('pm-music', { detail: song.title }));
  }

  // browsers only allow sound after the player touches the page: the first tune comes FIRST_WAIT seconds after the first tap or key
  const FIRST_WAIT = 60;
  function arm() {
    if (armed) return; armed = true;
    const go = () => { window.removeEventListener('pointerdown', go); window.removeEventListener('keydown', go); if (prefOn()) setTimeout(() => { if (!current) play() }, FIRST_WAIT * 1000) };
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
