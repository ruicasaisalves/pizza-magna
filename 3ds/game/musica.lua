--[[ The music on the 3DS: the browser game's tunes (music.js), recorded by tools/export_3ds_music.js into
     music/<id>.ogg, played with the same rules as music.js: a random order that alternates lo-fi and Italian
     (each kind shuffled apart, starting with either; when one kind runs out the rest of the other follow), every
     tune once, then a new deal, never the same tune twice in a row; the first tune a minute after the game starts
     (FIRST_WAIT), then a new tune every 3 minutes, with silence after each one; volume 1-5, 2 by default.
     The tunes are recorded at the browser's loudest level (5), so level v plays at LEVELS[v] / LEVELS[5]. ]]
local SONGS = require("musicdata")
local M = { on = true, vol = 2 }
local LEVELS = { .25, .5, 1, 1.6, 2.3 }
local FIRST_WAIT, EVERY = 60, 180
local ORDER, idx = {}, 0
local src, cur, startT, waitT = nil, nil, 0, FIRST_WAIT
local clock = 0

local function shuffle(l) for i = #l, 2, -1 do local j = math.random(i); l[i], l[j] = l[j], l[i] end; return l end
local function deal()
  local last = ORDER[#ORDER]
  local L, N = {}, {}
  for _, s in ipairs(SONGS) do if s.lofi then L[#L + 1] = s else N[#N + 1] = s end end
  shuffle(L); shuffle(N)
  local a, b = L, N
  if math.random() < .5 then a, b = N, L end
  ORDER = {}
  while #a > 0 or #b > 0 do
    if #a > 0 then ORDER[#ORDER + 1] = table.remove(a, 1) end
    a, b = b, a
  end
  if ORDER[1] == last and ORDER[3] then ORDER[1], ORDER[3] = ORDER[3], ORDER[1] end   -- positions 1 and 3 are the same kind
  idx = 0
end

local function stop() if src then src:stop(); src = nil end; cur = nil end
local function level() return LEVELS[M.vol] / LEVELS[5] end
function M.play()   -- the next tune in the order, now
  stop()
  if idx >= #ORDER then deal() end
  idx = idx + 1
  local s = ORDER[idx]
  local ok, x = pcall(love.audio.newSource, "music/" .. s.id .. ".ogg", "stream")
  if not ok then return end
  src, cur, startT, waitT = x, s, clock, nil
  src:setVolume(level()); src:play()
end
-- every frame: a tune that has ended leaves silence until 3 minutes after it began; then the next one
function M.update(dt)
  clock = clock + dt
  if not M.on then return end
  if src and not src:isPlaying() and clock - startT >= 1 then src = nil; cur = nil; waitT = math.max(2, EVERY - (clock - startT)) end
  if waitT and not src then
    waitT = waitT - dt
    if waitT <= 0 then M.play() end
  end
end
function M.setOn(on)
  M.on = on
  if on then M.play() else stop(); waitT = nil end
end
function M.setVol(v) M.vol = math.max(1, math.min(5, v)); if src then src:setVolume(level()) end end
function M.title() return cur and cur.title end
function M.init(on, vol)   -- from the save: on/off and the volume; the first tune comes FIRST_WAIT seconds later
  M.on = on ~= false; M.vol = math.max(1, math.min(5, tonumber(vol) or 2))
  deal(); waitT = M.on and FIRST_WAIT or nil
end
return M
