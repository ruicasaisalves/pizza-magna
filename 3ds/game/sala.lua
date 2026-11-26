--[[ The dining room on the touch screen, as in the browser's day (index.html: makeScene(), step(), drawRoom()),
     at half size: 16 px tiles, the starter room (the 3DS has no room editor), the cast characters.
     Art and layout come from tools/export_3ds_room.js (gfx/room.png, gfx/people.png, roomdata.lua).
     Positions are kept in the browser's 32 px units (x, y, and z for the depth), and drawn halved, OY pixels up
     (the top of the back wall is cut so the street fits). Customers come down the street; ours go in, wait in the
     queue, sit, a waiter brings the pizza from the counter, they eat and walk out with a face (happy, neutral or
     unhappy); the rest walk by, or on to the rival. ]]
local R = require("roomdata")
local M = {}
local T, COLS, ROWS = R.T, R.COLS, R.ROWS
local RW = COLS * T
M.OY = 16   -- half pixels cut from the top: the screen is 240 high, the room 272

local roomImg, peopleImg
local quads = {}
local function quad(img, x, y, w, h)
  local k = x .. "," .. y .. "," .. w .. "," .. h
  if not quads[k] then quads[k] = love.graphics.newQuad(x, y, w, h, img:getDimensions()) end
  return quads[k]
end
local SPR = {}   -- room sprites by key (pieces are drawn from the list)
for _, s in ipairs(R.sprites) do if s.key ~= "piece" then SPR[s.key] = s end end
function M.load()
  if not roomImg then roomImg = love.graphics.newImage("gfx/room.png"); peopleImg = love.graphics.newImage("gfx/people.png") end
end

-- the walking grid, and the shortest way between two tiles (as bfs() in index.html)
local solid = {}
for r = 0, ROWS - 1 do for c = 0, COLS - 1 do solid[r * COLS + c] = R.solid[r + 1]:sub(c + 1, c + 1) == "#" end end
local function bfs(from, to)
  local start, goal = from[2] * COLS + from[1], to[2] * COLS + to[1]
  if start == goal then return {} end
  local prev, q, h = { [start] = start }, { start }, 1
  while q[h] do
    local k = q[h]; h = h + 1
    if k == goal then break end
    local c, r = k % COLS, math.floor(k / COLS)
    for _, d in ipairs({ { 0, 1 }, { 1, 0 }, { 0, -1 }, { -1, 0 } }) do
      local nc, nr = c + d[1], r + d[2]
      if nc >= 0 and nr >= 0 and nc < COLS and nr < ROWS then
        local nk = nr * COLS + nc
        if prev[nk] == nil and (not solid[nk] or nk == goal) then prev[nk] = k; q[#q + 1] = nk end
      end
    end
  end
  if prev[goal] == nil then return { { x = to[1] * T, y = to[2] * T } } end
  local out = {}
  local k = goal
  while k ~= start do table.insert(out, 1, { x = (k % COLS) * T, y = math.floor(k / COLS) * T }); k = prev[k] end
  return out
end
local function tileOf(a) return { math.floor(a.x / T + .5), math.floor(a.y / T + .5) } end
local function moveAlong(o, dt, v)
  local d = v * dt
  o.walking = false
  while d > 0 and o.path[1] do
    local t = o.path[1]
    local dx, dy = t.x - o.x, t.y - o.y
    local L = math.sqrt(dx * dx + dy * dy)
    o.walking = true
    if math.abs(dx) > .01 or math.abs(dy) > .01 then
      o.dir = math.abs(dx) > math.abs(dy) and (dx > 0 and "right" or "left") or (dy > 0 and "down" or "up")
    end
    if L <= d then o.x, o.y = t.x, t.y; table.remove(o.path, 1); d = d - L
    else o.x, o.y = o.x + dx / L * d, o.y + dy / L * d; d = 0 end
  end
  if o.walking then o.ph = (o.ph or 0) + dt * 8 end
  return not o.path[1]
end

-- the staff's figures: a woman's name gets a woman's figure (staffV() in index.html), folders of assets/cast
local WOMEN = {}; for _, n in ipairs(R.STAFF_WOMEN) do WOMEN[n] = true end
local function staffV(p)
  local L = R.CAST_STAFF[p.r][WOMEN[p.n] and 2 or 1]
  return L[(p.v or 0) % #L + 1]
end
local spMul = function(sp) return 1 + .16 * ((sp or 3) - 3) end

-- the people of the room: the waiters in their corner and the cooks at the ovens (also before the doors open)
function M.scene(S, G)
  local sc = { people = {}, jobs = {}, waiters = {}, cooks = {}, seats = {} }
  for k, s in ipairs(R.seats) do sc.seats[k] = { s = s, occ = nil } end
  for i, p in ipairs(G.crew(S, "waiter")) do
    local h = R.WAITER_HOME[i]; if not h then break end
    sc.waiters[#sc.waiters + 1] = { x = h[1] * T, y = h[2] * T, home = h, path = {}, dir = "down", ph = 0, f = staffV(p) + 1, spd = spMul(p.sp) }
  end
  for i, p in ipairs(G.crew(S, "cook")) do
    local h = R.COOK_POS[i]; if not h then break end
    sc.cooks[#sc.cooks + 1] = { x = h[1] * T, y = h[2] * T, f = staffV(p) + 1 }
  end
  return sc
end

-- who comes in (guestLook() in index.html): one of the 21 looks, now and then the wizard or the goth, and the VIPs
-- from their stars on, once a day every few days
local function guestLook(a, e, S, DS)
  if e.target == "ours" then
    a.vips = a.vips or {}
    for _, v in ipairs(R.VIPS) do
      if not a.vips[v.id] and S.rep >= v.stars and (S.day + v.off) % v.every == 0 and a.t >= DS * v.from then a.vips[v.id] = true; return v.look end
    end
  end
  local r = math.random()
  return r < R.GUEST_P and R.GUEST_WIZARD or r < 2 * R.GUEST_P and R.GUEST_GOTH or math.random(0, 20)
end
local function bubble(a, x, y, s, c) a.bubbles[#a.bubbles + 1] = { x = x / 2, y = y / 2 - M.OY, s = s, c = c, life = 1.6 } end
local function spawn(a, e, S, DS)
  local left = e.target == "rival" or math.random() < .5
  local y = R.STREET_ROW * T + (e.target == "ours" and 0 or math.random(0, 16))
  local p = { e = e, x = left and -T or RW, y = y, look = guestLook(a, e, S, DS), v = 88 + math.random() * 24, st = "street", dir = left and "right" or "left", ph = math.random() * 4 }
  p.path = { { x = e.target == "ours" and R.DOOR[1] * T or e.target == "rival" and RW + T or (left and RW + T or -T), y = y } }
  a.sc.people[#a.sc.people + 1] = p
end

-- one step of the day (step() in index.html); c: the counters the top screen shows
function M.step(a, dt, S, DS, eur, colors)
  a.t = a.t + dt
  local sc, ev = a.sc, a.res.events
  while ev[a.idx] and ev[a.idx].t * DS <= a.t do spawn(a, ev[a.idx], S, DS); a.idx = a.idx + 1 end
  local qi, Q = 0, (#R.QUEUE > 0 and R.QUEUE or { R.DOOR_IN })
  for _, p in ipairs(sc.people) do
    if p.st == "queue" then
      local seat
      for _, s in ipairs(sc.seats) do if not s.occ then seat = s; break end end
      if seat then seat.occ = p; p.seat = seat; p.st = "toSeat"; p.path = bfs(tileOf(p), { seat.s.cx, seat.s.cy })
      else
        local spot = Q[math.min(qi, #Q - 1) + 1]; qi = qi + 1
        if not p.spot or p.spot[1] ~= spot[1] or p.spot[2] ~= spot[2] then p.spot = spot; p.path = bfs(tileOf(p), spot) end
        moveAlong(p, dt, p.v)
      end
    end
  end
  for _, p in ipairs(sc.people) do
    local st = p.st
    if st == "street" then
      if moveAlong(p, dt, p.v) then
        if p.e.target == "ours" then
          local o = p.e.out
          if o == "full" or o == "noseat" or o == "nostock" then
            a.cnt.left = a.cnt.left + 1; p.st = "leave"; p.path = { { x = p.x < RW / 2 and -T or RW + T, y = p.y } }
          else p.st = "queue"; p.spot = nil end
        else
          if p.e.target == "rival" then a.cnt.rival = a.cnt.rival + 1 end
          p.gone = true
        end
      end
    elseif st == "toSeat" then
      if moveAlong(p, dt, p.v) then p.st = "wait"; p.dir = p.seat.s.d; sc.jobs[#sc.jobs + 1] = p end
    elseif st == "wait" then
      if p.served then p.st = "eat"; p.timer = 2.6 end
    elseif st == "eat" then
      p.timer = p.timer - dt
      if p.timer <= 0 then
        a.cnt.served = a.cnt.served + 1; a.cnt.rev = a.cnt.rev + (p.e.price or 0)
        local h = p.e.out == "happy"
        bubble(a, p.x + 16, p.y - 44, "+" .. eur(p.e.price or 0), h and colors.good or colors.combo)
        local s = p.seat; s.occ = nil; p.st = "exit"
        p.path = bfs({ s.s.cx, s.s.cy }, { R.DOOR[1], R.STREET_ROW })
        p.path[#p.path + 1] = { x = math.random() < .5 and -T or RW + T, y = R.STREET_ROW * T }
      end
    elseif st == "exit" or st == "leave" then
      if moveAlong(p, dt, p.v) then p.gone = true end
    end
  end
  for k = #sc.people, 1, -1 do if sc.people[k].gone then table.remove(sc.people, k) end end
  for _, w in ipairs(sc.waiters) do
    if sc.jobs[1] and (not w.job or w.phase == "back") then w.job = table.remove(sc.jobs, 1); w.phase = "pick"; w.path = bfs(tileOf(w), R.PICK) end
    if not w.job then w.walking = false; if not w.path[1] then w.dir = "down" end
    else
      if (w.handoff or 0) > 0 then w.handoff = w.handoff - dt end
      if (w.pause or 0) > 0 then w.pause = w.pause - dt
      elseif moveAlong(w, dt, 164 * w.spd * (1 + math.min(1.2, #sc.jobs * .15))) then   -- they hurry when tables are waiting
        local s = w.job.seat.s
        if w.phase == "pick" then
          w.carry = true; w.phase = "go"; w.dir = "up"; w.pause = .25
          w.path = bfs(R.PICK, { s.cx, s.cy }); table.remove(w.path)   -- to the tile next to the seat
        elseif w.phase == "go" then
          w.job.served = true; w.carry = false; w.phase = "back"
          local tc = tileOf(w)
          local dx, dy = s.cx - tc[1], s.cy - tc[2]
          w.hdir = math.abs(dx) > math.abs(dy) and (dx > 0 and "right" or "left") or (dy > 0 and "down" or "up")
          w.handoff = R.PILOT_HANDOFF; w.pause = R.PILOT_HANDOFF; w.walking = false   -- face the customer
          w.path = bfs(tc, w.home)
        else w.job = nil; w.dir = "down" end
      end
    end
  end
  for k = #a.bubbles, 1, -1 do
    local b = a.bubbles[k]
    b.life = b.life - dt; b.y = b.y - dt * 9
    if b.life <= 0 then table.remove(a.bubbles, k) end
  end
  -- night falls once the doors are closed and everyone left inside is on the way out
  local closing = not ev[a.idx] and a.t >= DS
  if closing then
    for _, p in ipairs(sc.people) do
      if not (p.st == "exit" or p.st == "leave" or (p.st == "street" and p.e.target ~= "ours")) then closing = false; break end
    end
  end
  if closing then a.dusk = math.min(1, (a.dusk or 0) + dt / 1.5) end
  return closing and not sc.people[1] and a.dusk >= 1
end
-- after closing the room plays faster, the fuller the faster (as loop() in index.html)
function M.pace(a, DS)
  if a.t < DS then return 1 end
  local n = 0
  for _, p in ipairs(a.sc.people) do if p.st ~= "exit" and p.st ~= "leave" and p.st ~= "street" then n = n + 1 end end
  return math.min(16, 3 + n * .8)
end

-- drawing
local DIRS = { down = 0, right = 1, up = 2, left = 3 }
local OY = M.OY
local function hx(x) return math.floor(x / 2 + .5) end
local function hy(y) return math.floor(y / 2 + .5) - OY end
local function dxOf(key, row, col)   -- per-frame head nudges (PILOT_DX), halved
  local t = R.PILOT_DX[key]; t = t and t[tostring(row)]; local v = t and t[col + 1] or 0
  return v >= 0 and math.floor(v / 2) or -math.floor(-v / 2)
end
local function shadow(x, y)
  love.graphics.setColor(0, 0, 0, .24)
  love.graphics.rectangle("fill", hx(x) + 5, hy(y) + 14, 7, 1); love.graphics.rectangle("fill", hx(x) + 6, hy(y) + 13, 5, 1)
end
local function foot(origin, key, row, col, x, y)   -- a 16x29 cell with its feet on the bottom of the tile
  shadow(x, y)
  love.graphics.setColor(1, 1, 1)
  love.graphics.draw(peopleImg, quad(peopleImg, origin[1] + col * 16, origin[2] + row * 29, 16, 29), hx(x) + dxOf(key, row, col), hy(y) - 14)
end
local function sprite(s, x, y)   -- a room sprite at a half-pixel place
  love.graphics.setColor(1, 1, 1)
  love.graphics.draw(roomImg, quad(roomImg, s.q[1], s.q[2], s.q[3], s.q[4]), x, y)
end
-- a face over everyone walking out (faceArt() in index.html): yellow, a see-through ring, eyes and mouth
local RING = { good = { .27, .78, .24, .55 }, meh = { 1, .8, .16, .6 }, bad = { .78, .1, .06, .85 } }
function M.face(k, cx, top)   -- also in the report and the history
  local r = RING[k]
  love.graphics.setColor(r); love.graphics.circle("fill", cx, top + 5, 5)
  love.graphics.setColor(.35, .2, .06); love.graphics.circle("fill", cx, top + 5, 3.6)
  love.graphics.setColor(1, .85, .3); love.graphics.circle("fill", cx, top + 5, 3)
  love.graphics.setColor(.23, .12, .03)
  love.graphics.rectangle("fill", cx - 2, top + 3, 1, 2); love.graphics.rectangle("fill", cx + 1, top + 3, 1, 2)
  if k == "good" then love.graphics.rectangle("fill", cx - 2, top + 6, 1, 1); love.graphics.rectangle("fill", cx + 1, top + 6, 1, 1); love.graphics.rectangle("fill", cx - 1, top + 7, 2, 1)
  elseif k == "meh" then love.graphics.rectangle("fill", cx - 2, top + 7, 4, 1)
  else love.graphics.rectangle("fill", cx - 1, top + 6, 2, 1); love.graphics.rectangle("fill", cx - 2, top + 7, 1, 1); love.graphics.rectangle("fill", cx + 1, top + 7, 1, 1) end
end
local function faceOf(p)
  if p.st == "leave" or p.e.face == "bad" then return "bad" end
  return p.e.out == "happy" and "good" or "meh"
end

-- the room with its people; a: the running day or nil (the room before the doors open), sc: its scene
function M.draw(a, sc, S)
  M.load()
  love.graphics.setColor(1, 1, 1)
  love.graphics.draw(roomImg, quad(roomImg, 0, 0, 320, 272), 0, -OY)
  local L = {}
  local function add(z, fn) L[#L + 1] = { z = z, fn = fn } end
  for _, s in ipairs(R.sprites) do if s.key == "piece" then add(s.z, function() sprite(s, s.x, s.y - OY) end) end end
  local fr = a and math.floor(a.t * 6) or 0
  for i = 0, (S.ovens or 1) - 1 do
    local s = SPR["oven" .. ((fr + i) % 2)]
    add(s.z, function() sprite(s, s.x + i * R.OVEN_STEP / 2, s.y - OY) end)
  end
  local ready = a and math.min(3, #sc.jobs) or 0
  for k = 0, ready - 1 do add(256.3, function() sprite(SPR.pizza, hx(15 * T + k * 26), hy(7 * T - 22)) end) end
  for _, st in ipairs(sc.seats) do
    local p = st.occ
    if p and (p.st == "wait" or p.st == "eat") then
      local s, c = st.s, R.people_q.customers[p.look % #R.people_q.customers + 1].seated
      add(s.z, function()
        love.graphics.setColor(1, 1, 1)
        love.graphics.draw(peopleImg, quad(peopleImg, c[1], c[2] + DIRS[s.d] * 24, 16, s.d == "up" and 18 or 24), hx(s.x), hy(s.y))
      end)
      add(s.pz, function() sprite((p.st == "eat" and p.timer > 1) and SPR.pizza or SPR.plate, hx(s.px), hy(s.py)) end)
    end
  end
  for _, k in ipairs(sc.cooks) do
    add(k.y + T, function() foot(R.people_q.cooks[k.f], "cooks/" .. string.format("%02d", k.f) .. "/idle", 0, 0, k.x, k.y) end)
  end
  for _, w in ipairs(sc.waiters) do
    add(w.y + T, function()
      local hand = (w.handoff or 0) > 0
      local col = hand and 5 or (w.walking and 1 + math.floor(w.ph) % 4 or 0)
      local row = DIRS[hand and w.hdir or w.dir] * 2 + (w.carry and 1 or 0)
      foot(R.people_q.waiters[w.f], "waiters/" .. string.format("%02d", w.f) .. "/service", row, col, w.x, w.y)
    end)
  end
  for _, p in ipairs(sc.people) do
    if p.st ~= "wait" and p.st ~= "eat" then
      add(p.y + T, function()
        local n = p.look % #R.people_q.customers + 1
        foot(R.people_q.customers[n].walk, "customers/" .. string.format("%02d", n) .. "/walk", DIRS[p.dir], p.walking and 1 + math.floor(p.ph) % 4 or 0, p.x, p.y)
      end)
    end
  end
  table.sort(L, function(u, v) return u.z < v.z end)
  for _, d in ipairs(L) do d.fn() end
  if a and a.dusk then love.graphics.setColor(30 / 255, 22 / 255, 70 / 255, .4 * a.dusk); love.graphics.rectangle("fill", 0, 0, 320, 240) end
  if a then
    for _, p in ipairs(sc.people) do
      if p.st == "exit" or p.st == "leave" then M.face(faceOf(p), hx(p.x + 16), hy(p.y) - 26) end
    end
  end
end

return M
