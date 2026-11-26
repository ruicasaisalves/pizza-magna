--[[ The restaurant, ported from index.html: the street simulation (simulateDay), the close of the day (finishDay),
     the contest (resolveContest) and the shop. The logic follows the browser game; change it here too when it
     changes there. Differences on the 3DS for now: one room (the browser game's starter room, exported to
     data.lua as ROOM), no pantry (every topping is bought on the day at MANAGER_MARKUP, as the browser game's
     manager does, with no manager fee), no manager setting prices or hiring, and one shop (no City). ]]
local P = require("pizza")
local D, t = P.D, P.t
local G = {}

local function r2(v) return math.floor(v * 100 + .5) / 100 end
local function round(v) return math.floor(v + .5) end
local function clamp(v, a, b) return math.max(a, math.min(b, v)) end
local function noise() return (math.random() + math.random() + math.random() - 1.5) * 1.6 end
local function shuffle(l) for i = #l, 2, -1 do local j = math.random(i); l[i], l[j] = l[j], l[i] end; return l end
local MEH_BAND = require("roomdata").MEH_BAND   -- served but not happy: within it neutral, further below unhappy (as index.html)
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

--[[ Staff (as in index.html): pizzaiolos ("cook") and waiters, each a person {id, n = name, r = role, sp = speed 1-5,
     sk = second skill 1-5 (cooking or charm), w = wage a day, v = look}. A cook's speed sets the kitchen's pizzas a
     day (COOK_CAP at 3/5), a waiter's the customers served (WAITER_CAP); the day serves the smaller of the two. The
     second skill adds to each customer's satisfaction (crewSat). New people come every day (candidates()). ]]
function G.spMul(sp) return 1 + .16 * (sp - 3) end
function G.wageOf(r, sp, sk) return (r == "cook" and D.SALARY or D.WAITER_SALARY) + 2 * (sp - 3) + 2 * (sk - 3) end
function G.crew(S, r) local out = {}; for _, p in ipairs(S.staff) do if p.r == r then out[#out + 1] = p end end; return out end
function G.wages(S) local w = 0; for _, p in ipairs(S.staff) do w = w + p.w end; return w end
local function avgSkill(S, r) local c, n = G.crew(S, r), 0; for _, p in ipairs(c) do n = n + p.sk end; return #c > 0 and n / #c or 3 end
function G.newPerson(S, r, sp, sk, also)
  local used = {}
  for _, l in ipairs({ S.staff or {}, S.cands or {}, also or {} }) do for _, p in ipairs(l) do used[p.n] = true end end
  local free = {}; for _, n in ipairs(D.STAFF_NAMES) do if not used[n] then free[#free + 1] = n end end
  if #free == 0 then free = D.STAFF_NAMES end
  local function star() return 1 + math.floor((math.random() + math.random()) * 2.5) end   -- 1-5, mostly 2-4
  sp, sk = sp or star(), sk or star()
  return { id = tostring(math.random(1e8)), n = free[math.random(#free)], r = r, sp = sp, sk = sk,
    w = G.wageOf(r, sp, sk) + math.random(-1, 1), v = math.random(0, 11) }
end
-- a new game's team, and old saves' count of pizzaiolos: average people at the base wage
function G.startStaff(S, cooks, waiters)
  local out = {}
  for i = 1, cooks + waiters do
    local r = i <= cooks and "cook" or "waiter"
    local p = G.newPerson(S, r, 3, 3, out); p.w = r == "cook" and D.SALARY or D.WAITER_SALARY
    out[#out + 1] = p
  end
  return out
end
-- today's people looking for work: three pizzaiolos and three waiters, new every day
function G.candidates(S)
  if S.candDay ~= S.day then
    S.cands, S.candDay = {}, S.day
    for _, r in ipairs({ "cook", "cook", "cook", "waiter", "waiter", "waiter" }) do S.cands[#S.cands + 1] = G.newPerson(S, r) end
  end
  return S.cands
end
function G.hire(S, id)
  for k, c in ipairs(G.candidates(S)) do
    if c.id == id then
      if #G.crew(S, c.r) >= D.MAX_STAFF[c.r] or S.money < D.HIRE_COST then return nil end
      S.money = r2(S.money - D.HIRE_COST); S.staff[#S.staff + 1] = c; table.remove(S.cands, k)
      return c
    end
  end
end
function G.letGo(S, id)   -- never the last of a role
  for k, p in ipairs(S.staff) do
    if p.id == id and #G.crew(S, p.r) > 1 then table.remove(S.staff, k); return p end
  end
end
function G.capacity(S)   -- the kitchen
  local k = 0; for _, p in ipairs(G.crew(S, "cook")) do k = k + D.COOK_CAP * G.spMul(p.sp) end
  return math.min(S.ovens * D.OVEN_CAP, round(k))
end
function G.serviceCap(S)   -- the dining room
  local k = 0; for _, p in ipairs(G.crew(S, "waiter")) do k = k + D.WAITER_CAP * G.spMul(p.sp) end
  return round(k)
end
-- a new shop's street: foot traffic 1-5 (3 is like the first shop's)
local function trafficMul(S) local sh = S.shops and S.shops[S.cur]; return sh and sh.traffic and .55 + sh.traffic * .15 or 1 end
function G.expected(S) return round((20 + S.rep * 8) * D.WK_MUL[(S.day - 1) % 7 + 1] * (S.ads and 1.45 or 1) * trafficMul(S)) end
function G.weekday(day) return (P.lang() == "pt" and D.WD or D.WD_EN)[(day - 1) % 7 + 1] end
function G.themeFor(day) return D.THEME_IDS[(day / 5 - 1) % #D.THEME_IDS + 1] end
function G.nextContestDay(S) return math.ceil(S.day / 5) * 5 end

local function segMix(S)
  local sh = S.shops and S.shops[S.cur]
  local H = sh and sh.hood and D.CITY.HOODS[sh.hood]   -- a new shop: its neighbourhood's customers
  local m = H and { estudante = H.mix[1] / 100, familia = H.mix[2] / 100, turista = H.mix[3] / 100, gourmet = H.mix[4] / 100 }
    or { estudante = .36, familia = .32, turista = .18, gourmet = .14 }
  local atm, tot = D.ROOM.atm, 0
  for k, v in pairs(m) do m[k] = v * (.6 + atm[k] / 100 * .8); tot = tot + m[k] end   -- a room a group likes brings more of it
  for k in pairs(m) do m[k] = m[k] / tot end
  return m
end
-- happy quotes per customer group (qh.<group>1 … qh.<group>N in I18N; QH_N in index.html)
local QH_N = 0
while D.I18N.en["qh.estudante" .. (QH_N + 1)] do QH_N = QH_N + 1 end
local function pizzaNeeds(p) local n = {}; for _, x in ipairs(p.pieces) do n[x.i] = (n[x.i] or 0) + P.pieceGrams(x) end; return n end
local function gramPrice(id) return P.ingC(id) / (D.GRAMS[id] or 10) end

-- How a customer chooses among the pizzas they'd have (utilities u): each with a chance that grows with u (a logit,
-- PICK_T wide), so the best pizza for them sells most, but one a little behind still sells some. Only pizzas within
-- SLACK of the best count. pickPizza() in index.html.
local PICK_T, SLACK = 1.2, 3
local function pickW(us)
  local mx, w = -1e9, {}
  for _, u in ipairs(us) do mx = math.max(mx, u) end
  for i, u in ipairs(us) do w[i] = u >= mx - SLACK and math.exp((u - mx) / PICK_T) or 0 end
  return w
end
local function pickPizza(pool)
  if #pool == 0 then return nil end
  local us = {}; for i, o in ipairs(pool) do us[i] = o.u end
  local w, tot = pickW(us), 0
  for _, x in ipairs(w) do tot = tot + x end
  local x = math.random() * tot
  for i, o in ipairs(pool) do x = x - w[i]; if x <= 0 then return o end end
  return pool[#pool]
end
-- Who picks each pizza: for each customer group, the share of those who come in that would choose each pizza of
-- the menu (as pickPizza() does, noise included; its own fixed-seed generator so the game's random stays untouched),
-- and the group each pizza suits best. menuShares() in index.html.
function G.menuShares(S, anOf)
  local M, A, sh = S.menu, {}, {}
  for j, p in ipairs(M) do A[j] = anOf(p) end
  local sd = 777
  local function rnd() sd = (sd * 1103515245 + 12345) % 2147483648; return sd / 2147483648 end
  local function nz() return (rnd() + rnd() + rnd() - 1.5) * 1.6 end
  local K = 100
  for _, g in ipairs(D.SEG_ORDER) do
    local n = {}; for j = 1, #M do n[j] = 0 end
    for _ = 1, K do
      local us = {}; for j, p in ipairs(M) do us[j] = custU(g, A[j].appeal[g], p.price, A[j].cost) + nz() end
      local w, tot = pickW(us), 0
      for _, x in ipairs(w) do tot = tot + x end
      for j, x in ipairs(w) do n[j] = n[j] + x / tot end
    end
    for j = 1, #M do n[j] = n[j] / K end
    sh[g] = n
  end
  return { A = A, sh = sh }
end
-- why pizza i is not the first choice of the group it suits best (nil when it is): menu.why.* in I18N
function G.menuWhy(S, W, i)
  local M, A, sh = S.menu, W.A, W.sh
  if #M < 2 then return nil end
  local function edge(g) local o = -1e9; for j, b in ipairs(A) do if j ~= i then o = math.max(o, b.appeal[g]) end end; return A[i].appeal[g] - o end
  local g = D.SEG_ORDER[1]
  for _, k in ipairs(D.SEG_ORDER) do if edge(k) > edge(g) then g = k end end
  local w
  for j = 1, #M do if j ~= i and (not w or sh[g][j] > sh[g][w]) then w = j end end
  if sh[g][w] <= sh[g][i] then return nil end
  local dA, dP = A[w].appeal[g] - A[i].appeal[g], M[i].price - M[w].price
  local k = dA >= 3 and dP > .25 and "both" or dA >= 3 and "taste" or dP > .25 and dA > -3 and "price" or dP > .25 and "dear" or "value"
  return t("menu.why." .. k, { g = t("seg." .. g), x = M[w].name, p = P.eur(dP) })
end

-- Reputation gets harder as it grows (as in index.html): happy at HAPPY_BASE + HAPPY_STAR a star, and a good day's
-- gain shrinks near the top (repGain); losses are not softened.
-- HARD_REP: on since 0.03e, as on the web (false would go back to happy at 62 and no shrinking gains).
local HARD_REP, HAPPY_BASE, HAPPY_STAR, REP_TOP = true, 55, 5, 5.25
function G.happyAt(S) if not HARD_REP then return 62 end return HAPPY_BASE + S.rep * HAPPY_STAR end
function G.repGain(S, d) if HARD_REP and d > 0 then return d * math.max(.12, (REP_TOP - S.rep) / (REP_TOP - 1)) end return d end

function G.simulateDay(S)
  local menuA = {}
  for _, p in ipairs(S.menu) do menuA[#menuA + 1] = { p = p, a = P.analyze(p), need = pizzaNeeds(p), base = D.DOUGHS[p.dough].c + D.SAUCES[p.sauce].c } end
  local mix, cap, r, N = segMix(S), math.min(G.capacity(S), G.serviceCap(S)), S.rival, G.expected(S)
  local crewSat = (avgSkill(S, "cook") - 3) + (avgSkill(S, "waiter") - 3)   -- a skilled pizzaiolo's hand and a charming waiter
  local TH, REGULARS = 4.2, .45
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
    repDelta = 0, happy = 0, unhappy = 0, meh = 0, sad = 0, sales = {}, bySeg = {}, quotes = {}, N = N, cap = cap, seats = D.ROOM.seats }
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
      -- which pizza: any within SLACK of what they'd accept, by chance weighted on how much they like it
      local pool = {}
      for _, o in ipairs(opts) do if o.u >= bar - SLACK then pool[#pool + 1] = o end end
      local pk = pickPizza(pool)
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
        res.bySeg[seg] = res.bySeg[seg] or {}; res.bySeg[seg][m.p.id] = (res.bySeg[seg][m.p.id] or 0) + 1
        local ap = m.a.appeal[seg]
        local over = m.p.price - G.fairPrice(ap, m.a.cost)
        local sat = ap + noise() * 5 - math.max(0, over) * 7 + (atm[seg] - 35) / 7 + crewSat
        if sat >= G.happyAt(S) then
          res.happy = res.happy + 1; res.repDelta = res.repDelta + .008; e.out = "happy"
          if math.random() < .25 then quote(seg, t("qh." .. seg .. math.random(QH_N), { x = m.p.name })) end
        else
          res.unhappy = res.unhappy + 1; res.repDelta = res.repDelta - .03; e.out = "meh"
          e.face = sat >= G.happyAt(S) - MEH_BAND and "meh" or "bad"   -- the face they leave with: neutral or unhappy
          if e.face == "meh" then res.meh = res.meh + 1 else res.sad = res.sad + 1 end
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
  local p = G.anyPizza(S, S.contestEntry)
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

--[[ Several shops (the City), as in index.html: the open shop's fields (SHOP_KEYS) live at the root of S, the
     others in S.shops[i].data; S.shops[i] = {hood, lot, traffic, owned, data}; S.cur is the open one. The first shop
     has no hood (the original customer mix) and pays RENT; a rented one its lot's rent, a bought one none. ]]
G.SHOP_KEYS = { "rep", "ovens", "staff", "ads", "menu", "rival", "lastSales", "hist", "supplier" }
function G.openShop(S, i)
  if i == S.cur or not S.shops[i] or not S.shops[i].data then return false end
  local park = {}; for _, k in ipairs(G.SHOP_KEYS) do park[k] = S[k] end
  S.shops[S.cur].data = park
  for _, k in ipairs(G.SHOP_KEYS) do S[k] = S.shops[i].data[k] end
  S.shops[i].data = nil; S.cur = i
  return true
end
function G.shopName(S, i)
  local sh = S.shops[i or S.cur]
  return (sh and sh.hood) and ("Pizza Magna · " .. t("hood." .. sh.hood)) or "Pizza Magna"
end
function G.rentOf(S, i)
  local sh = S.shops[i]
  if not sh or not sh.hood then return D.RENT end
  return sh.owned and 0 or D.CITY.LOTS[sh.lot].rent
end
-- a pizza by id on any shop's menu (the open shop first): the contest entry may come from another shop
function G.anyPizza(S, id)
  if not id then return nil end
  for _, p in ipairs(S.menu) do if p.id == id then return p end end
  for _, sh in ipairs(S.shops or {}) do if sh.data then for _, p in ipairs(sh.data.menu) do if p.id == id then return p end end end end
end
-- Rivals' strategies (rival.style: the first shop's is classic, a new shop's comes from its neighbourhood, HOOD_STYLE).
-- When you beat it, it cuts its price with chance cut (not below pMin), or else improves its pizzas by qStep (up to
-- qMax; a premium rival also raises its price); when it beats you it raises its price (up to pMax). promo(day): the
-- days of its 2-for-1 (weekdays: (day-1)%7, 0 Monday ... 6 Sunday). RSTYLE in index.html.
local RSTYLE = {
  classic = { cut = .5, qStep = 4, qMax = 85, pMin = 5, pMax = 9.5, promo = function(d) return d % 6 == 0 end },
  cheap = { cut = .8, qStep = 2, qMax = 70, pMin = 4.5, pMax = 8, promo = function(d) return d % 4 == 0 end },
  tourist = { cut = .4, qStep = 3, qMax = 85, pMin = 6, pMax = 11, promo = function(d) local w = (d - 1) % 7; return w == 4 or w == 5 end },
  family = { cut = .5, qStep = 3, qMax = 80, pMin = 5.5, pMax = 10, promo = function(d) return (d - 1) % 7 == 6 end },
  gourmet = { cut = 0, qStep = 5, qMax = 95, pMin = 9, pMax = 16, promo = function() return false end, premium = true },
}
-- one shop's side of the day, on the open shop's fields: takings and costs, reputation, history and its rival
-- (news only for the shop being watched: the others run in the background)
function G.shopDay(S, res, day, watched)
  local r, sal, rent = S.rival, G.wages(S), G.rentOf(S, S.cur)
  local profit = r2(res.revenue - res.ingCost - rent - sal)
  S.money = r2(S.money + profit)
  local repBefore = S.rep
  S.rep = r2(clamp(S.rep + G.repGain(S, clamp(res.repDelta, -.4, .25)), 0, 5))
  S.lastSales = res.sales
  -- the day goes into the history (HIST_DAYS days kept), with its best seller by name
  local top, topN = "", 0
  for _, p in ipairs(S.menu) do local n = res.sales[p.id] or 0; if n > topN then top, topN = p.name, n end end
  S.hist[#S.hist + 1] = { d = day, n = res.served, N = res.N, rv = res.toRival, p = profit, v = res.revenue, r = S.rep, top = top, topN = topN,
    f = { res.happy, res.meh or 0, (res.sad or 0) + res.full + res.noseat + res.nostock } }   -- how they left: happy, neutral, unhappy
  while #S.hist > D.HIST_DAYS do table.remove(S.hist, 1) end
  S.ads = false
  local nw = {}
  r.promo = false
  local st = RSTYLE[r.style or "classic"] or RSTYLE.classic
  if res.served > res.toRival * 1.3 and res.served > 8 then
    if math.random() < st.cut and r.price > st.pMin then r.price = r2(r.price - .5); nw[#nw + 1] = news("nw.cut", { r = r.name, p = P.eur(r.price) })
    elseif r.q < st.qMax then
      r.q = math.min(st.qMax, r.q + st.qStep); nw[#nw + 1] = news("nw.cook", { r = r.name })
      if st.premium and r.price < st.pMax then r.price = r2(r.price + .5) end
    end
  elseif res.toRival > res.served * 1.5 and r.price < st.pMax then r.price = r2(r.price + .5); nw[#nw + 1] = news("nw.raise", { r = r.name, p = P.eur(r.price) }) end
  if day % 4 == 0 and r.q < st.qMax then r.q = r.q + 1 end
  if st.promo(day + 1) then r.promo = true; nw[#nw + 1] = news("nw.promo", { r = r.name }) end
  return { profit = profit, sal = sal, rent = rent, repBefore = repBefore, repAfter = S.rep, news = watched and nw or {} }
end
-- the shops not being watched run their day in the background; one with no menu stays closed but still pays its
-- rent and wages
function G.otherShopsDay(S, day)
  local here, out = S.cur, {}
  for i = 1, #S.shops do
    if i ~= here and S.shops[i].data then
      G.openShop(S, i)
      local open = #S.menu > 0
      local res = open and G.simulateDay(S) or { served = 0, N = 0, toRival = 0, revenue = 0, ingCost = 0, repDelta = 0, sales = {} }
      local r = G.shopDay(S, res, day, false)
      out[#out + 1] = { name = G.shopName(S, i), open = open, served = res.served, N = res.N, profit = r.profit }
    end
  end
  G.openShop(S, here)
  return out
end

function G.finishDay(S, res)
  local day = S.day
  local own = G.shopDay(S, res, day, true)
  local others = G.otherShopsDay(S, day)
  local contest
  if day % 5 == 0 then if S.contestEntry then contest = G.resolveContest(S) end; S.contestEntry = nil end
  local interest = r2((S.loan or 0) * D.BANK_RATE)   -- the bank's interest, every day
  if interest > 0 then S.money = r2(S.money - interest) end
  local nw = own.news
  S.day = S.day + 1
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
  local quotes, seen = {}, {}
  for _, x in ipairs(shuffle(res.quotes)) do   -- no line twice
    if not seen[x[2]] and #quotes < 3 then seen[x[2]] = true; quotes[#quotes + 1] = x end
  end
  local goal = false
  if D.GOAL_ON and not S.goalDone and S.money >= D.GOAL_MONEY and S.rep >= D.GOAL_REP then S.goalDone = true; goal = true end
  return { res = res, profit = own.profit, sal = own.sal, rent = own.rent, repBefore = own.repBefore, repAfter = own.repAfter, contest = contest,
    quotes = quotes, day = day, goal = goal, interest = interest, others = others }
end

--[[ The City (city.js, exported to D.CITY): with CITY_CASH of your own money (cash minus what you owe) rent a lot
     (its rent every day, works paid now) or buy one (price and works now, no rent). On the 3DS a new shop opens with
     the starter room (there is no room editor) and a copy of the open shop's menu (there is no recipe book); its
     neighbourhood's customers and street, the nearest rival and a reputation of 1 star plus a tenth of the best. ]]
function G.ownMoney(S) return r2(S.money - (S.loan or 0)) end
function G.lotShop(S, i) for k, sh in ipairs(S.shops) do if sh.lot == i then return k end end end
function G.lotKind(S, i)
  local l = D.CITY.LOTS[i]
  if G.lotShop(S, i) then return "mine" end
  return l.kind == "mine" and "taken" or l.kind
end
function G.lotCost(l, buy) return (buy and l.price or 0) + (l.cond == "works" and l.works or 0) end
local function copyMenu(menu)
  local out = {}
  for _, p in ipairs(menu) do
    local c = { id = p.id, name = p.name, dough = p.dough, sauce = p.sauce, price = p.price, pieces = {} }
    for k, x in ipairs(p.pieces) do local y = {}; for kk, vv in pairs(x) do y[kk] = vv end; c.pieces[k] = y end
    out[#out + 1] = c
  end
  return out
end
function G.openLot(S, i, buy)   -- nil and an I18N key when it can't
  local l = D.CITY.LOTS[i]
  if G.lotKind(S, i) ~= (buy and "sale" or "rent") then return nil end
  if G.ownMoney(S) < D.CITY_CASH then return nil, "city.need" end
  local cost = G.lotCost(l, buy)
  if S.money < cost then return nil, "rm.nomoney" end
  S.money = r2(S.money - cost)
  local best = S.rep
  for _, sh in ipairs(S.shops) do if sh.data then best = math.max(best, sh.data.rep) end end
  local rv, rd
  for _, x in ipairs(D.CITY.LOTS) do
    if x.kind == "rival" then
      local d = math.sqrt((x.x - l.x) ^ 2 + (x.y - l.y) ^ 2)
      if not rd or d < rd then rv, rd = x, d end
    end
  end
  local RH = D.RIVAL_HOOD[l.hood]
  S.shops[#S.shops + 1] = { hood = l.hood, lot = i, traffic = l.traffic, owned = buy and true or false, data = {
    rep = r2(1 + (best - 1) * .1), ovens = 1, staff = G.startStaff(S, 1, 1), ads = false, menu = copyMenu(S.menu),
    rival = { name = rv.name, q = RH.q, price = RH.price, style = D.HOOD_STYLE[l.hood], promo = false },
    lastSales = {}, hist = {}, supplier = 1 } }
  G.openShop(S, #S.shops)
  return true
end
function G.closeShop(S, k)   -- a rented shop's lease ends; a bought one sells for SELL_SHARE of its price; never the last
  local sh = S.shops[k]
  if #S.shops < 2 or not sh then return nil end
  if k == S.cur then G.openShop(S, k == 1 and 2 or 1) end   -- leave it first: the shop being closed must be parked
  local gain = sh.owned and math.floor(D.CITY.LOTS[sh.lot].price * D.SELL_SHARE + .5) or 0
  local name = G.shopName(S, k)
  local cur = S.shops[S.cur]
  table.remove(S.shops, k)
  for n, x in ipairs(S.shops) do if x == cur then S.cur = n end end
  if gain > 0 then S.money = r2(S.money + gain) end
  return name, gain
end
G.news = news

-- the bank: borrow in steps up to BANK_MAX; BANK_RATE of what you owe is charged every day (finishDay)
function G.borrow(S, v)
  if (S.loan or 0) + v > D.BANK_MAX then return false end
  S.loan = r2((S.loan or 0) + v); S.money = r2(S.money + v); return true
end
function G.repay(S, v)   -- v = nil: all of it
  local owe = S.loan or 0
  v = math.min(v or owe, owe)
  if v <= 0 or S.money < v then return nil end
  S.loan = r2(owe - v); S.money = r2(S.money - v); return v
end

-- the shop
G.SHOP = {
  { id = "oven", cost = function(S) return 500 + S.ovens * 300 end, ok = function(S) return S.ovens < 3 end,
    lvl = function(S) return t("shop.oven.l", { n = S.ovens }) end, d = function() return t("shop.oven.d", { n = D.OVEN_CAP }) end,
    buy = function(S) S.ovens = S.ovens + 1 end },
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
