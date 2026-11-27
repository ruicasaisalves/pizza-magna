--[[ The room's rules, as in index.html ("room design"): what stands where (S.room = {floor, wall, walls = 6 wall
     pieces or false, items = {{id, c, r}}, lights}), what fits, which tables a waiter can reach, the seats, the
     atmosphere for each customer group, and the walking grid of the day. Ported by hand from roomEditable(),
     RESERVED, roomOcc(), roomFits(), roomAnalyse(), starterRoom() and buildMap(); the pieces (ITEMS, FLOORS, WALLS)
     come from roomdata.lua (tools/export_3ds_room.js). ]]
local R = require("roomdata")
local M = {}
local T, COLS, ROWS = R.T, R.COLS, R.ROWS
local function key(c, r) return r * COLS + c end
local function clamp(v, a, b) return math.max(a, math.min(b, v)) end
M.ITEMS, M.FLOORS, M.WALLS = R.ITEMS, R.FLOORS, R.WALLS

function M.editable(c, r) return c >= 0 and c < COLS and r >= 2 and r <= 13 and not (c >= 12 and r <= 7) end
local RESERVED = { [key(R.PICK[1], R.PICK[2])] = true, [key(R.DOOR_IN[1], R.DOOR_IN[2])] = true, [key(R.DOOR_IN[1] + 1, R.DOOR_IN[2])] = true }
for _, h in ipairs(R.WAITER_HOME) do RESERVED[key(h[1], h[2])] = true end   -- the counter, the waiters' corner, the way in

-- the starter room (a copy), and a room made safe to use (old saves have none)
local function copy(v) if type(v) ~= "table" then return v end; local o = {}; for k, x in pairs(v) do o[k] = copy(x) end; return o end
function M.starter() return copy(R.STARTER) end
function M.ensure(room)
  if type(room) ~= "table" or type(room.items) ~= "table" then return M.starter() end
  room.floor = M.FLOORS[room.floor] and room.floor or "check"; room.wall = M.WALLS[room.wall] and room.wall or "cream"
  room.walls = type(room.walls) == "table" and room.walls or {}
  for i = 1, R.WALL_SLOTS do if not M.ITEMS[room.walls[i] or ""] then room.walls[i] = false end end
  local ok = {}; for _, it in ipairs(room.items) do if M.ITEMS[it.id] then ok[#ok + 1] = it end end; room.items = ok
  return room
end

-- the tiles each piece takes (its mask: '#' blocks), and the rugs (they block nothing but other rugs)
function M.occ(room, skip)
  local g, rugs = {}, {}
  for _, it in ipairs(room.items) do
    if it ~= skip then
      local d = M.ITEMS[it.id]
      for j, row in ipairs(d.mask) do
        for i = 1, #row do
          local k = key(it.c + i - 1, it.r + j - 1)
          if row:sub(i, i) == "#" then g[k] = it elseif d.rug then rugs[k] = it end
        end
      end
    end
  end
  return g, rugs
end
function M.fits(room, id, c, r, skip)
  local d = M.ITEMS[id]
  local g, rugs = M.occ(room, skip)
  for j = 0, d.h - 1 do
    for i = 0, d.w - 1 do
      local cc, rr = c + i, r + j
      if not M.editable(cc, rr) then return false end
      local k = key(cc, rr)
      if d.rug then if rugs[k] then return false end
      elseif d.mask[j + 1]:sub(i + 1, i + 1) == "#" and (g[k] or RESERVED[k]) then return false end
    end
  end
  return true
end

-- seats, tables a waiter can reach, the kitchen's way, and the atmosphere for each group (roomAnalyse())
function M.analyse(room)
  local g = M.occ(room)
  local seen, q, h = {}, {}, 1
  for _, c in ipairs({ R.DOOR_IN[1], R.DOOR_IN[1] + 1 }) do local k = key(c, R.DOOR_IN[2]); seen[k] = true; q[#q + 1] = k end   -- floor reachable from the door
  while q[h] do
    local k = q[h]; h = h + 1
    local c, r = k % COLS, math.floor(k / COLS)
    for _, d in ipairs({ { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } }) do
      local nc, nr = c + d[1], r + d[2]
      local nk = key(nc, nr)
      if M.editable(nc, nr) and not seen[nk] and not g[nk] then seen[nk] = true; q[#q + 1] = nk end
    end
  end
  local blocked, nblocked, seats, tables = {}, 0, 0, 0
  for _, it in ipairs(room.items) do
    local d = M.ITEMS[it.id]
    if d.cat == "table" then
      local ok = false
      for j = -1, d.h do
        for i = -1, d.w do
          local inside = i >= 0 and j >= 0 and i < d.w and j < d.h
          if not (inside and d.mask[j + 1]:sub(i + 1, i + 1) == "#") and seen[key(it.c + i, it.r + j)] then ok = true end
        end
      end
      if ok then tables = tables + 1; seats = seats + d.n else blocked[it] = true; nblocked = nblocked + 1 end   -- a table counts only if a waiter can get next to it
    end
  end
  local kitchenOk = seen[key(R.PICK[1], R.PICK[2])] == true
  local total, free = 0, 0
  for r = 2, 13 do for c = 0, COLS - 1 do if M.editable(c, r) then total = total + 1; if not g[key(c, r)] then free = free + 1 end end end end
  local freeShare = free / total
  local sum, byStyle = { 0, 0, 0, 0 }, { tasca = 0, tratt = 0, moder = 0, luxo = 0 }
  local function addApp(d, w)
    w = w or 1
    for i = 1, 4 do sum[i] = sum[i] + d.app[i] * w end
    byStyle[d.style] = byStyle[d.style] + math.max(30, d.price)
  end
  addApp(M.FLOORS[room.floor], 2); addApp(M.WALLS[room.wall], 2)
  for _, it in ipairs(room.items) do addApp(M.ITEMS[it.id]) end
  for i = 1, R.WALL_SLOTS do local w = room.walls[i]; if w then addApp(M.ITEMS[w]) end end
  if room.lights then addApp(M.ITEMS.luzes) end
  local tot, dom = 0, "tratt"
  for k, v in pairs(byStyle) do tot = tot + v; if v > byStyle[dom] then dom = k end end
  local share = byStyle[dom] / tot
  local bonus = { 0, 0, 0, 0 }
  if share >= .5 then for i = 1, 4 do bonus[i] = R.STYLE_BONUS[dom][i] * (share - .5) * 2 end end
  local crowd = freeShare < .42 and math.floor((.42 - freeShare) * 120 + .5) or 0
  local atm = {}
  for i, k in ipairs(R.SEGK) do atm[k] = clamp(math.floor(20 + sum[i] * .9 + bonus[i] - crowd + .5), 0, 100) end
  return { blocked = blocked, nblocked = nblocked, kitchenOk = kitchenOk, seats = seats, tables = tables, atm = atm, freeShare = freeShare, dom = dom }
end

-- the day's walking grid, its seats (where the sitter is drawn, the plate, the tile to walk to) and the queue (buildMap())
function M.map(room)
  local solid = {}
  local D0, D1 = R.DOOR[1], R.DOOR[1] + 1
  for r = 0, ROWS - 1 do
    for c = 0, COLS - 1 do
      if r < 2 or (r == 14 and c ~= D0 and c ~= D1) or r > 15 or (r == 15 and c ~= D0 and c ~= D1) then solid[key(c, r)] = true end
      if c >= 12 and r >= 2 and r <= 7 then solid[key(c, r)] = true end
    end
  end
  local A = M.analyse(room)
  local seats = {}
  for _, it in ipairs(room.items) do
    local d = M.ITEMS[it.id]
    for j, row in ipairs(d.mask) do for i = 1, #row do if row:sub(i, i) == "#" then solid[key(it.c + i - 1, it.r + j - 1)] = true end end end
    if d.cat == "table" and not A.blocked[it] and d.layout then
      local lay, x0, y0 = d.layout, it.c * T, it.r * T
      local tx, ty, rx, ry = lay.top[1], lay.top[2], lay.top[3], lay.top[4]
      local tz = 0; for _, q in ipairs(lay.parts) do if q[1]:sub(1, 2) == "t_" then tz = q[4] end end
      for _, st in ipairs(lay.seats) do
        local qx = st.d == "right" and tx - rx + 14 or st.d == "left" and tx + rx - 14 or (st.chair and tx or st.p[1] + 16)
        local qy = st.d == "down" and ty - ry + 9 or st.d == "up" and ty + ry - 9 or ty
        seats[#seats + 1] = { cx = it.c + clamp(math.floor((st.p[1] + 16) / T), 0, d.w - 1), cy = it.r + clamp(math.floor((st.p[2] + 40) / T), 0, d.h - 1),
          d = st.d, x = x0 + st.p[1], y = y0 + st.p[2], z = y0 + st.p[3], px = x0 + math.floor(qx + .5) - 12, py = y0 + math.floor(qy + .5) - 8, pz = y0 + tz + .2 }
      end
    end
  end
  local queue = {}
  for _, p in ipairs(R.QUEUE) do if not solid[key(p[1], p[2])] then queue[#queue + 1] = p end end
  return { solid = solid, seats = seats, queue = queue, A = A }
end

-- the piece under a point of the room (32 px units): furniture before rugs, the one in front first (edHit())
function M.hit(room, x, y)
  if y < 2 * T and x < 12 * T then return nil end
  local c, r = math.floor(x / T), math.floor(y / T)
  local best
  for _, it in ipairs(room.items) do
    local d = M.ITEMS[it.id]
    if c >= it.c and c < it.c + d.w and r >= it.r and r < it.r + d.h then
      if not best then best = it
      else
        local br, ir = M.ITEMS[best.id].rug and 0 or 1, d.rug and 0 or 1
        if ir > br or (ir == br and it.r > best.r) then best = it end
      end
    end
  end
  return best
end
return M
