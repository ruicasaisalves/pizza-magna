--[[ The restaurant, ported from index.html: the street simulation (simulateDay), the close of the day (finishDay),
     the contest (resolveContest) and the shop. The logic follows the browser game; change it here too when it
     changes there. Differences on the 3DS for now: one room (the browser game's starter room, exported to
     data.lua as ROOM), no pantry (every topping is bought on the day at MANAGER_MARKUP, as the browser game's
     manager does, with no manager fee) and no manager setting prices or hiring. ]]
local P = require("pizza")
local D, t = P.D, P.t
local G = {}

local function r2(v) return math.floor(v * 100 + .5) / 100 end
local function round(v) return math.floor(v + .5) end
local function clamp(v, a, b) return math.max(a, math.min(b, v)) end
local function noise() return (math.random() + math.random() + math.random() - 1.5) * 1.6 end
local function shuffle(l) for i = #l, 2, -1 do local j = math.random(i); l[i], l[j] = l[j], l[i] end; return l end
G.r2 = r2

local baseCost = D.DOUGHS.fina.c + D.SAUCES.tomate.c
local function perceivedCost(cost) local e = math.max(0, cost - baseCost); return D.VALUE_CAP * (1 - math.exp(-e / D.VALUE_CAP)) end
function G.fairPrice(a, cost) return math.max(3, D.BASE_PRICE + perceivedCost(cost or baseCost + 1) * D.MARKUP + (a - 50) * D.APPEAL_W) end
local function custU(seg, ap, price, cost)
  local v = G.fairPrice(ap, cost) - price
  if seg == "estudante" then return ap / 10 - 1.5 * (price - 7) + .25 * v end
  if seg == "familia" then return ap / 10 + 1.15 * v end
  if seg == "gourmet" then return ap / 6 + .35 * v - .15 * (price - 10) end
  return ap / 10 - .5 * (price - 8) + .5 * v   -- tourists
end

function G.capacity(S) return math.min(S.ovens * D.OVEN_CAP, S.cooks * D.COOK_CAP) end
function G.expected(S) return round((20 + S.rep * 8) * D.WK_MUL[(S.day - 1) % 7 + 1] * (S.ads and 1.45 or 1)) end
function G.weekday(day) return (P.lang() == "pt" and D.WD or D.WD_EN)[(day - 1) % 7 + 1] end
function G.themeFor(day) return D.THEME_IDS[(day / 5 - 1) % #D.THEME_IDS + 1] end
function G.nextContestDay(S) return math.ceil(S.day / 5) * 5 end
function G.waiters(S) return math.min(4, S.cooks + 1) end

local function segMix()
  local atm, m, tot = D.ROOM.atm, { estudante = .36, familia = .32, turista = .18, gourmet = .14 }, 0
  for k, v in pairs(m) do m[k] = v * (.6 + atm[k] / 100 * .8); tot = tot + m[k] end   -- a room a group likes brings more of it
  for k in pairs(m) do m[k] = m[k] / tot end
  return m
end
local function pizzaNeeds(p) local n = {}; for _, x in ipairs(p.pieces) do n[x.i] = (n[x.i] or 0) + P.pieceGrams(x) end; return n end
local function gramPrice(id) return P.ingC(id) / (D.GRAMS[id] or 10) end

function G.simulateDay(S)
  local menuA = {}
  for _, p in ipairs(S.menu) do menuA[#menuA + 1] = { p = p, a = P.analyze(p), need = pizzaNeeds(p), base = D.DOUGHS[p.dough].c + D.SAUCES[p.sauce].c } end
  local mix, cap, r, N = segMix(), G.capacity(S), S.rival, G.expected(S)
  local TH, REGULARS, CURIOUS, SLACK = 4.2, .45, .2, 3
  local atm, EAT, WAIT = D.ROOM.atm, .18, .04
  local seatFree = {}; for k = 1, D.ROOM.seats do seatFree[k] = 0 end
  local bought = 0
  local function useStock(m)   -- no pantry on the 3DS yet: everything is bought on the spot
    local v = 0
    for id, want in pairs(m.need) do local b = want * gramPrice(id) * D.MANAGER_MARKUP; v = v + b; bought = bought + b end
    return v
  end
  local function g() return (math.random() + math.random() + math.random() - 1.5) * 2 end
  local arrivals = {}   -- two rushes, lunch and dinner, and a few in between
  for i = 1, N do
    local x = math.random()
    arrivals[i] = clamp(x < .45 and .27 + g() * .06 or x < .9 and .66 + g() * .07 or math.random() * .9, .02, .9)
  end
  table.sort(arrivals)
  local res = { events = {}, served = 0, toRival = 0, full = 0, noseat = 0, nostock = 0, passed = 0, revenue = 0, ingCost = 0,
    repDelta = 0, happy = 0, unhappy = 0, sales = {}, quotes = {}, N = N, cap = cap, seats = D.ROOM.seats }
  local function pickSeg()
    local x = math.random()
    for _, k in ipairs(D.SEG_ORDER) do x = x - mix[k]; if x <= 0 then return k end end
    return "familia"
  end
  local function quote(seg, s) res.quotes[#res.quotes + 1] = { seg, s } end
  for i = 1, N do
    local seg, at = pickSeg(), arrivals[i]
    local deco = (atm[seg] - 35) / 25 + (S.rep - 2.5) * .3   -- the room's atmosphere for this group, and the reputation
    local opts = {}
    for _, m in ipairs(menuA) do opts[#opts + 1] = { m = m, u = custU(seg, m.a.appeal[seg], m.p.price, m.a.cost) + noise() + deco } end
    table.sort(opts, function(a, b) return a.u > b.u end)
    local best, bu = opts[1] and opts[1].m, opts[1] and opts[1].u or -1e9
    local ra = clamp(r.q + D.RIVAL_BIAS[seg], 0, 100)
    local ru = custU(seg, ra, r.price, baseCost + 1) + noise() + (r.promo and 1.5 or 0)
    local e = { t = at, seg = seg }
    -- regulars (about half the street) come back unless the pizza is poor or overpriced, whatever the rival does
    local regular = math.random() < REGULARS
    local bar = regular and TH - 2.5 or math.max(ru, TH)
    if best and bu >= bar then
      e.target = "ours"
      local pk
      for _, o in ipairs(opts) do if o.u >= bar then pk = o; break end end
      -- some newcomers are curious and pick any pizza not far below what they'd accept
      if not regular and math.random() < CURIOUS then
        local pool = {}
        for _, o in ipairs(opts) do if o.u >= bar - SLACK then pool[#pool + 1] = o end end
        if #pool > 1 then pk = pool[math.random(#pool)] end
      end
      local m = pk and pk.m
      local k
      for j = 1, #seatFree do if not k or seatFree[j] < seatFree[k] then k = j end end   -- the seat that frees up first
      if not m then res.nostock = res.nostock + 1; res.repDelta = res.repDelta - .006; e.out = "nostock"
      elseif res.served < cap and (not k or seatFree[k] > at + WAIT) then
        res.noseat = res.noseat + 1; res.repDelta = res.repDelta - .012; e.out = "noseat"
        if math.random() < .3 then quote(seg, t("qt.noseat")) end
      elseif res.served < cap then
        seatFree[k] = math.max(at, seatFree[k]) + EAT
        res.served = res.served + 1; res.revenue = res.revenue + m.p.price; res.ingCost = res.ingCost + m.base + useStock(m)
        res.sales[m.p.id] = (res.sales[m.p.id] or 0) + 1; e.price = m.p.price
        local ap = m.a.appeal[seg]
        local over = m.p.price - G.fairPrice(ap, m.a.cost)
        local sat = ap + noise() * 5 - math.max(0, over) * 7 + (atm[seg] - 35) / 7
        if sat >= 62 then
          res.happy = res.happy + 1; res.repDelta = res.repDelta + .008; e.out = "happy"
          if math.random() < .25 then quote(seg, t("qh." .. seg .. (math.random() < .5 and 1 or 2), { x = m.p.name })) end
        else
          res.unhappy = res.unhappy + 1; res.repDelta = res.repDelta - .03; e.out = "meh"
          local bad
          for _, n in ipairs(m.a.notes) do if n[1] == "bad" and n[3] and not bad then bad = n[3] end end
          quote(seg, over > 1.5 and t("qt.dear", { p = P.eur(m.p.price) }) or bad or t("qt.meh"))
        end
      else
        res.full = res.full + 1; res.repDelta = res.repDelta - .012; e.out = "full"
        if math.random() < .3 then quote(seg, t("qt.full")) end
      end
    elseif ru >= TH then
      e.target = "rival"; res.toRival = res.toRival + 1
      if best and math.random() < .12 then
        quote(seg, t(r.promo and "qt.promo" or (best.p.price > r.price + 1.5 and "qt.cheaper" or "qt.taste"), { r = r.name }))
      end
    else e.target = "none"; res.passed = res.passed + 1 end
    res.events[#res.events + 1] = e
  end
  table.sort(res.events, function(a, b) return a.t < b.t end)
  res.revenue, res.ingCost, res.bought = r2(res.revenue), r2(res.ingCost), r2(bought)
  return res
end

function G.resolveContest(S)
  local day, th = S.day, G.themeFor(S.day)
  local p
  for _, x in ipairs(S.menu) do if x.id == S.contestEntry then p = x end end
  if not p then return nil end
  local mine = P.contestScore(th, p)
  local base = math.min(92, 50 + day * 1.1)
  local names = {}
  for _, n in ipairs(D.NPCS) do if n ~= S.rival.name then names[#names + 1] = n end end
  shuffle(names)
  local rows = {}
  for k = 1, 3 do rows[#rows + 1] = { n = names[k], s = round(base + math.random() * 16 - 8) } end
  rows[#rows + 1] = { n = S.rival.name, s = round(base + math.random() * 16 - 8) }
  local me = { n = "Pizza Magna · " .. p.name, s = round(mine.s), me = true, dq = mine.dq }
  rows[#rows + 1] = me
  table.sort(rows, function(a, b) return a.s > b.s end)
  local pos
  for k, x in ipairs(rows) do if x == me then pos = k end end
  local prize, rep = ({ 600, 250, 80 })[pos] or 0, ({ .4, .2, .1 })[pos] or 0
  S.money = S.money + prize; S.rep = clamp(S.rep + rep, 0, 5)
  table.insert(S.contestLog, 1, { day = day, theme = th, pizza = p.name, pos = pos, prize = prize })
  while #S.contestLog > 6 do table.remove(S.contestLog) end
  return { th = th, rows = rows, pos = pos, prize = prize, rep = rep, dq = mine.dq }
end

-- news are kept as {k = I18N key, v = values}; a value "@key" is a name looked up when shown (the language can change)
local function news(k, v) return { k = k, v = v or {} } end
function G.newsText(n)
  local v = {}
  for k, x in pairs(n.v) do v[k] = (type(x) == "string" and x:sub(1, 1) == "@") and t(x:sub(2)) or x end
  return t(n.k, v)
end

function G.finishDay(S, res)
  local r, sal = S.rival, S.cooks * D.SALARY
  local profit = r2(res.revenue - res.ingCost - D.RENT - sal)
  S.money = r2(S.money + profit)
  local repBefore = S.rep
  S.rep = clamp(S.rep + clamp(res.repDelta, -.4, .25), 0, 5)
  S.lastSales = res.sales
  local contest
  if S.day % 5 == 0 then if S.contestEntry then contest = G.resolveContest(S) end; S.contestEntry = nil end
  S.ads = false
  local nw = {}
  r.promo = false
  if res.served > res.toRival * 1.3 and res.served > 8 then
    if math.random() < .5 and r.price > 5 then r.price = r2(r.price - .5); nw[#nw + 1] = news("nw.cut", { r = r.name, p = P.eur(r.price) })
    elseif r.q < 85 then r.q = r.q + 4; nw[#nw + 1] = news("nw.cook", { r = r.name }) end
  elseif res.toRival > res.served * 1.5 and r.price < 9.5 then r.price = r2(r.price + .5); nw[#nw + 1] = news("nw.raise", { r = r.name, p = P.eur(r.price) }) end
  if S.day % 4 == 0 and r.q < 85 then r.q = r.q + 1 end
  S.day = S.day + 1
  if S.day % 6 == 0 then r.promo = true; nw[#nw + 1] = news("nw.promo", { r = r.name }) end
  if S.day % 5 == 0 then nw[#nw + 1] = news("nw.ct", { x = "@th." .. G.themeFor(S.day) })
  elseif S.day % 5 == 4 then nw[#nw + 1] = news("nw.ct1", { x = "@th." .. G.themeFor(S.day + 1) }) end
  if S.day % 7 == 1 then
    local w = P.week(S.day)
    nw[#nw + 1] = news("wk.news", { x = "@ing." .. w.ing, c = "@combo." .. w.combo })
    nw[#nw + 1] = news("wk.newslow", { x = "@ing." .. w.low })
  end
  if #nw == 0 then nw[1] = news("nw.q" .. (S.day % 3 + 1)) end
  for k = #nw, 1, -1 do table.insert(S.news, 1, nw[k]) end
  while #S.news > 8 do table.remove(S.news) end
  if S.money < -500 then S.over = true end
  local q = shuffle(res.quotes)
  local quotes = { q[1], q[2], q[3] }
  local goal = false
  if not S.goalDone and S.money >= D.GOAL_MONEY and S.rep >= D.GOAL_REP then S.goalDone = true; goal = true end
  return { res = res, profit = profit, sal = sal, repBefore = repBefore, repAfter = S.rep, contest = contest, quotes = quotes, day = S.day - 1, goal = goal }
end
G.news = news

-- the shop
G.SHOP = {
  { id = "oven", cost = function(S) return 500 + S.ovens * 300 end, ok = function(S) return S.ovens < 3 end,
    lvl = function(S) return t("shop.oven.l", { n = S.ovens }) end, d = function() return t("shop.oven.d", { n = D.OVEN_CAP }) end,
    buy = function(S) S.ovens = S.ovens + 1 end },
  { id = "cook", cost = function() return 100 end, ok = function(S) return S.cooks < 5 end,
    lvl = function(S) return t("shop.cook.l", { n = S.cooks }) end, d = function() return t("shop.cook.d", { n = D.COOK_CAP, w = "$" .. D.SALARY }) end,
    buy = function(S) S.cooks = S.cooks + 1 end },
  { id = "ads", cost = function() return 120 end, ok = function(S) return not S.ads end,
    lvl = function(S) return t(S.ads and "shop.ads.on" or "shop.ads.l") end, d = function() return t("shop.ads.d") end,
    buy = function(S) S.ads = true end },
}
function G.weekOf(d) return math.floor((d - 1) / 7) end
-- the market study: a topping one group loves (one of its 8 best) and a combo not found yet (studyTips())
function G.studyTips(S)
  local seg = D.SEG_ORDER[math.random(#D.SEG_ORDER)]
  local CASA, EXOTIC = {}, {}
  for _, x in ipairs(D.CASA) do CASA[x] = true end
  for _, x in ipairs(D.EXOTIC) do EXOTIC[x] = true end
  local score = {}
  for _, id in ipairs(D.ING_ORDER) do
    local s = 0
    for _, tg in ipairs(D.ING[id].t) do s = s + (D.SEG[seg].w[tg] or 0) end
    if CASA[id] then s = s + (D.SEG[seg].w.casa or 0) end
    if EXOTIC[id] then s = s + (D.SEG[seg].w.exotico or 0) end
    score[id] = s
  end
  local ids = {}
  for _, id in ipairs(D.ING_ORDER) do if id ~= "mozzarella" then ids[#ids + 1] = id end end
  table.sort(ids, function(a, b) if score[a] ~= score[b] then return score[a] > score[b] end; return a < b end)
  local ing = ids[math.random(math.min(8, #ids))]
  local left = {}
  for _, c in ipairs(D.COMBOS) do
    local known = P.has(S.found, c.id)
    for _, x in ipairs(S.tips) do if x.combo == c.id then known = true end end
    if c.q > 0 and not known then left[#left + 1] = c.id end
  end
  return { day = S.day, seg = seg, ing = ing, combo = left[1] and left[math.random(#left)] or nil }
end
function G.comboReq(id)
  for _, c in ipairs(D.COMBOS) do
    if c.id == id then
      local parts = {}
      for _, r in ipairs(c.req) do
        parts[#parts + 1] = r:sub(1, 2) == "s:" and t("k.book.sauce", { x = t("sauce." .. r:sub(3)):lower() }) or P.ingName(r)
      end
      return table.concat(parts, " + ")
    end
  end
  return ""
end
function G.tipText(x)
  local out = { t("study.ing", { g = t("seg." .. x.seg), x = P.ingName(x.ing) }) }
  if x.combo then out[2] = t("study.combo", { x = t("combo." .. x.combo), r = G.comboReq(x.combo) }) end
  return out
end

return G
