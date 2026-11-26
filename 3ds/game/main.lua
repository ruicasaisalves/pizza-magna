--[[ Pizza Magna for the Nintendo 3DS (LÖVE Potion), prototype: the Kitchen and the Menu.
     Kitchen. Bottom screen (touch): the bench, as in the browser game (320 wide, title strip on top, pizza,
     bowls, LCD). Top screen: the topping picker, dough and sauce, and the analysis (quality, cost, appeal, notes).
     Menu. Top screen: the house menu, one row a pizza. Bottom screen: the chosen pizza, its price
     (- / +), quality, cost and margin, and the buttons to edit, rename or remove it.
     Day: the LCD and the news on top, the street below (customers walk to our door or the rival's), then the
     close-of-day report. Contest: the next theme on top, the pizzas to enter below. Shop: ovens, pizzaiolos,
     flyers, supplier, market study. SELECT goes to the next screen (and L/R, outside the Kitchen).
     On a PC (LÖVE 11/12) the window shows the top screen above the bottom one, and the mouse is the stylus. ]]
local P = require("pizza")
local G = require("day")
local D, A, t = P.D, P.A, P.t

local CONSOLE = love._console ~= nil or love.system.getOS() == "Horizon" or love.system.getOS() == "3DS"
local BOTTOM_X, BOTTOM_Y = 40, 240   -- where the bottom screen sits in the PC window

-- text only the 3DS port has (the browser game has no buttons to explain)
local L3 = {
  en = { keys1 = "</> topping   L/R group   Up dough   Down sauce",
         keys2 = "A cut   X turn   B undo   Y clear   SELECT next screen   START quit",
         mkeys1 = "Up/Down pizza   </> price   A edit   X rename   Y remove",
         nav = "L/R or SELECT other screens   START quit", rename = "RENAME",
         dkeys = "A open the doors", drun = "</> speed   B pause   A skip to closing", rkeys = "A continue",
         ckeys = "Up/Down pizza   A enter it", skeys = "Up/Down choose   A buy / choose   touch: hire, let go, bank",
         hkeys = "Y sales history", hback = "Y back to the day",
         citykeys = "D-pad or map: move   A rent, buy, go   Y close, sell   X zoom",
         },
  pt = { keys1 = "</> ingrediente   L/R grupo   Cima massa   Baixo molho",
         keys2 = "A picar   X rodar   B desfazer   Y limpar   SELECT ecrã seguinte   START sair",
         mkeys1 = "Cima/Baixo pizza   </> preço   A editar   X nome   Y remover",
         nav = "L/R ou SELECT outros ecrãs   START sair", rename = "MUDAR NOME",
         dkeys = "A abrir portas", drun = "</> velocidade   B pausa   A saltar para o fecho", rkeys = "A continuar",
         ckeys = "Cima/Baixo pizza   A inscrever", skeys = "Cima/Baixo escolher   A comprar / escolher   toque: contratar, dispensar, banco",
         hkeys = "Y histórico de vendas", hback = "Y voltar ao dia",
         citykeys = "Cruz ou mapa: mover   A arrendar, comprar, ir   Y fechar, vender   X zoom",
         },
}
local function l3(k) return L3[P.lang()][k] end
local MINE_LOT = 1   -- the first shop's lot on the city map
for i, l in ipairs(D.CITY.LOTS) do if l.kind == "mine" then MINE_LOT = i end end

-- ---------------------------------------------------------------- state and save
--[[ S.name/S.editing: the pizza on the bench (no name yet = "New pizza"; editing = id of the menu pizza it came from).
     S.menu: the house menu, {id, name, dough, sauce, pieces, price}, as in the browser game. ]]
local S = { dough = "napo", sauce = "tomate", pieces = {}, sel = "fiambre", cut = "w", rot = {}, found = {}, lang = nil,
  name = nil, editing = nil, menu = nil, tab = "kitchen", msel = 1, nextId = 1, csel = 1, ssel = 1 }
local anim, report = nil, nil   -- the day running in the street; the close-of-day report on screen
local histOn = false             -- the Day's top screen shows the sales history instead of the LCD (Y)
local cleared = nil          -- the pizza the bin just cleared: undo on an empty bench brings it back
local dirty, saveTimer = false, 0
local toasts = {}
local an                     -- analysis of the pizza on the bench (recomputed on every change)

-- save.txt: one "key=value" a line; each menu pizza is a "pizza=" line of tab-separated fields
-- the shops on one "shops=" line, as a Lua table literal (the parked ones carry their data; pieces packed)
local function ser(v)
  local ty = type(v)
  if ty == "number" then return string.format("%.4g", v) == tostring(v) and tostring(v) or string.format("%.6f", v) end
  if ty == "boolean" then return tostring(v) end
  if ty == "string" then return '"' .. v:gsub("\\", "\\\\"):gsub('"', '\\"'):gsub("\n", "\\n"):gsub("\r", "") .. '"' end
  if ty ~= "table" then return "nil" end
  local out = {}
  for k, x in pairs(v) do
    if k ~= "an" then out[#out + 1] = (type(k) == "number" and ("[" .. k .. "]") or ("[" .. ser(k) .. "]")) .. "=" .. ser(x) end
  end
  return "{" .. table.concat(out, ",") .. "}"
end
local function shopsLine()
  local list = {}
  for i, sh in ipairs(S.shops) do
    local x = { hood = sh.hood, lot = sh.lot, traffic = sh.traffic, owned = sh.owned }
    if sh.data then
      local d = {}
      for k, v in pairs(sh.data) do d[k] = v end
      d.menu = {}
      for _, p in ipairs(sh.data.menu) do d.menu[#d.menu + 1] = { id = p.id, name = p.name, dough = p.dough, sauce = p.sauce, price = p.price, pk = P.packPieces(p.pieces) } end
      x.data = d
    end
    list[i] = x
  end
  return "shops=" .. ser(list)
end
local function readShops(val)
  local f = (loadstring or load)("return " .. val)
  local ok, list = pcall(f or error)
  if not ok or type(list) ~= "table" then return nil end
  for _, sh in ipairs(list) do
    if sh.data then
      for _, p in ipairs(sh.data.menu or {}) do
        local pieces = {}
        pcall(function() pieces = P.unpackPieces(p.pk or "") end)
        p.pieces, p.pk = pieces, nil
      end
      sh.data.hist, sh.data.lastSales, sh.data.staff = sh.data.hist or {}, sh.data.lastSales or {}, sh.data.staff or {}
    end
  end
  return list
end
local function save()
  local rot = {}
  for k, v in pairs(S.rot) do rot[#rot + 1] = k .. ":" .. v end
  local lines = {
    "lang=" .. P.lang(), "dough=" .. S.dough, "sauce=" .. S.sauce, "sel=" .. S.sel, "cut=" .. S.cut,
    "rot=" .. table.concat(rot, ","), "found=" .. table.concat(S.found, ","), "pieces=" .. P.packPieces(S.pieces),
    "name=" .. (S.name or ""), "editing=" .. (S.editing or ""), "tab=" .. S.tab, "msel=" .. S.msel, "nextid=" .. S.nextId, "menu=1",
    "day=" .. S.day, "money=" .. string.format("%.2f", S.money), "rep=" .. string.format("%.4f", S.rep), "ovens=" .. S.ovens,
    "loan=" .. string.format("%.2f", S.loan or 0), "candday=" .. (S.candDay or ""), "ads=" .. (S.ads and 1 or 0), "supplier=" .. S.supplier, "entry=" .. (S.contestEntry or ""),
    "studyweek=" .. S.studyWeek, "over=" .. (S.over and 1 or 0), "goal=" .. (S.goalDone and 1 or 0),
    "rival=" .. table.concat({ S.rival.name, S.rival.q, string.format("%.2f", S.rival.price), S.rival.promo and 1 or 0 }, "\t"),
  }
  local sales = {}
  for id, n in pairs(S.lastSales) do sales[#sales + 1] = id .. ":" .. n end
  lines[#lines + 1] = "sales=" .. table.concat(sales, ",")
  lines[#lines + 1] = "cur=" .. S.cur
  lines[#lines + 1] = shopsLine()
  for _, n in ipairs(S.news) do
    local f = { n.k }
    for k, v in pairs(n.v) do f[#f + 1] = k .. "=" .. tostring(v):gsub("[\t\n]", " ") end
    lines[#lines + 1] = "news=" .. table.concat(f, "\t")
  end
  -- people: id, name, role, speed, second skill, wage, look (staff = the team, cand = today's candidates)
  for _, l in ipairs({ { "staff", S.staff }, { "cand", S.cands or {} } }) do
    for _, x in ipairs(l[2]) do lines[#lines + 1] = l[1] .. "=" .. table.concat({ x.id, x.n, x.r, x.sp, x.sk, x.w, x.v }, "\t") end
  end
  for _, h in ipairs(S.hist) do
    lines[#lines + 1] = "hist=" .. table.concat({ h.d, h.n, h.N, h.rv, string.format("%.2f", h.p), string.format("%.2f", h.v), string.format("%.2f", h.r), (h.top or ""):gsub("[\t\n]", " "), h.topN or 0, h.f and h.f[1] or "", h.f and h.f[2] or "", h.f and h.f[3] or "" }, "\t")
  end
  for _, c in ipairs(S.contestLog) do lines[#lines + 1] = "ctlog=" .. table.concat({ c.day, c.theme, c.pizza, c.pos, c.prize }, "\t") end
  for _, x in ipairs(S.tips) do lines[#lines + 1] = "tip=" .. table.concat({ x.day, x.seg, x.ing, x.combo or "" }, "\t") end
  for _, p in ipairs(S.menu) do
    lines[#lines + 1] = "pizza=" .. table.concat({ p.id, string.format("%.2f", p.price), p.dough, p.sauce, p.name, P.packPieces(p.pieces) }, "\t")
  end
  love.filesystem.write("save.txt", table.concat(lines, "\n") .. "\n")
  dirty = false
end
local function load()
  local ok, txt = pcall(love.filesystem.read, "save.txt")
  if not ok or not txt then return end
  local v, menu, news, ctlog, tips, people, hist = {}, {}, {}, {}, {}, { staff = {}, cand = {} }, {}
  local function fields(val) local f = {}; for x in (val .. "\t"):gmatch("([^\t]*)\t") do f[#f + 1] = x end; return f end
  for line in txt:gmatch("[^\n]+") do
    local k, val = line:match("^(%w+)=(.*)$")
    if k == "news" then
      local f = fields(val)
      local n = G.news(f[1])
      for q = 2, #f do local a, b = f[q]:match("^(%w+)=(.*)$"); if a then n.v[a] = b end end
      news[#news + 1] = n
    elseif k == "ctlog" then
      local f = fields(val)
      ctlog[#ctlog + 1] = { day = tonumber(f[1]) or 0, theme = f[2], pizza = f[3], pos = tonumber(f[4]) or 0, prize = tonumber(f[5]) or 0 }
    elseif k == "staff" or k == "cand" then
      local f = fields(val)
      if f[3] == "cook" or f[3] == "waiter" then
        local n = function(i, d) return math.max(1, math.min(5, tonumber(f[i]) or d)) end
        people[k][#people[k] + 1] = { id = f[1], n = f[2], r = f[3], sp = n(4, 3), sk = n(5, 3), w = tonumber(f[6]) or 30, v = tonumber(f[7]) or 0 }
      end
    elseif k == "hist" then
      local f = fields(val)
      local n = function(i) return tonumber(f[i]) or 0 end
      hist[#hist + 1] = { d = n(1), n = n(2), N = n(3), rv = n(4), p = n(5), v = n(6), r = n(7), top = f[8] or "", topN = n(9),
        f = (f[10] or "") ~= "" and { n(10), n(11), n(12) } or nil }   -- how they left (days before the faces have none)
    elseif k == "tip" then
      local f = fields(val)
      if D.SEG[f[2]] and D.ING[f[3]] then tips[#tips + 1] = { day = tonumber(f[1]) or 1, seg = f[2], ing = f[3], combo = f[4] ~= "" and f[4] or nil } end
    elseif k == "pizza" then
      local f = {}
      for x in (val .. "\t"):gmatch("([^\t]*)\t") do f[#f + 1] = x end
      if #f >= 6 and D.DOUGHS[f[3]] and D.SAUCES[f[4]] then
        local pieces = {}
        pcall(function() pieces = P.unpackPieces(f[6]) end)
        menu[#menu + 1] = { id = f[1], price = tonumber(f[2]) or 9, dough = f[3], sauce = f[4], name = f[5], pieces = pieces }
      end
    elseif k == "shops" then v.shops = readShops(val)
    elseif k then v[k] = val end
  end
  if v.menu then S.menu = menu end   -- saves from before the Menu get the starter pizzas
  if v.name and v.name ~= "" then S.name = v.name end
  if v.editing and v.editing ~= "" then S.editing = v.editing end
  if v.tab then S.tab = v.tab end
  S.msel = tonumber(v.msel) or 1
  S.nextId = tonumber(v.nextid) or 1
  if v.day then   -- saves from before the restaurant start a new game in load (S.day stays nil)
    S.day, S.money, S.rep = tonumber(v.day) or 1, tonumber(v.money) or 1000, tonumber(v.rep) or 1
    S.ovens, S.ads, S.loan = tonumber(v.ovens) or 1, v.ads == "1", tonumber(v.loan) or 0
    -- the team; saves from before the staff profiles had a count of pizzaiolos (waiters were free): average people
    if #people.staff > 0 then S.staff = people.staff
    else local n = tonumber(v.cooks) or 1; S.staff = G.startStaff(S, n, math.ceil(n * 2 / 3)) end
    S.cands, S.candDay, S.hist = people.cand, tonumber(v.candday), hist
    -- the shops (saves from before the City: one shop on the first lot)
    S.shops = type(v.shops) == "table" and #v.shops > 0 and v.shops or { { lot = MINE_LOT } }
    S.cur = math.max(1, math.min(#S.shops, tonumber(v.cur) or 1))
    S.shops[S.cur].data = nil
    S.supplier = D.SUPPLIER[tonumber(v.supplier)] and tonumber(v.supplier) or 1
    S.contestEntry = v.entry ~= "" and v.entry or nil
    S.studyWeek, S.over, S.goalDone = tonumber(v.studyweek) or -1, v.over == "1", v.goal == "1"
    local f = fields(v.rival or "")
    S.rival = { name = f[1] ~= "" and f[1] or "Pizza Rápida", q = tonumber(f[2]) or 52, price = tonumber(f[3]) or 7, promo = f[4] == "1" }
    S.lastSales = {}
    for id, n in (v.sales or ""):gmatch("([%w_]+):(%d+)") do S.lastSales[id] = tonumber(n) end
    S.news, S.contestLog, S.tips = news, ctlog, tips
  end
  if not ({ kitchen = 1, menu = 1, day = 1, contest = 1, shop = 1, city = 1 })[S.tab] then S.tab = "kitchen" end
  if v.lang then S.lang = v.lang end
  if v.dough and D.DOUGHS[v.dough] then S.dough = v.dough end
  if v.sauce and D.SAUCES[v.sauce] then S.sauce = v.sauce end
  if v.sel and D.ING[v.sel] then S.sel = v.sel end
  if v.cut == "g" then S.cut = "g" end
  for k, n in (v.rot or ""):gmatch("([%w_]+):(%d)") do if D.ING[k] then S.rot[k] = tonumber(n) end end
  for id in (v.found or ""):gmatch("[%w_]+") do S.found[#S.found + 1] = id end
  if v.pieces and v.pieces ~= "" then pcall(function() S.pieces = P.unpackPieces(v.pieces) end) end
end

local function toast(s)   -- a new message cuts the one on screen short, so a "press again" never waits in a queue
  if toasts[1] and toasts[1].time > .6 then toasts[1].time = .6 end
  toasts[#toasts + 1] = { s = s, time = 3 }
end
local function r2(v) return math.floor(v * 100 + .5) / 100 end

-- the three pizzas a new game starts with (freshState() in index.html; spread() lays a topping out in a spiral)
local function spread(id, n, rad, seed)
  local out = {}
  local function fx(v, d) local m = 10 ^ d; return (v < 0 and -1 or 1) * math.floor(math.abs(v) * m + .5) / m end
  for k = 0, n - 1 do
    local a, r = (k + seed) * 2.39996, rad * math.sqrt((k + .5) / n)
    out[#out + 1] = { i = id, x = fx(math.cos(a) * r, 3), y = fx(math.sin(a) * r, 3), r = fx((k * 1.7 + seed) % 6.28, 2) }
  end
  return out
end
local function join(...) local out = {}; for _, l in ipairs({ ... }) do for _, x in ipairs(l) do out[#out + 1] = x end end; return out end
local function starterMenu()
  local cheese = function() return spread("mozzarella", 11, .74, 0) end
  S.menu = {
    { id = "p1", name = "Margherita da Casa", dough = "napo", sauce = "tomate", price = 9, pieces = join(cheese(), spread("manjericao", 6, .62, 3)) },
    { id = "p2", name = t("start.fc"), dough = "napo", sauce = "tomate", price = 9, pieces = join(cheese(), spread("fiambre", 7, .66, 1), spread("cogumelos", 7, .6, 4)) },
    { id = "p3", name = t("start.pep"), dough = "napo", sauce = "tomate", price = 9, pieces = join(cheese(), spread("pepperoni", 9, .66, 2), spread("oregaos", 5, .55, 5)) },
  }
  S.nextId = 4
end
-- the restaurant at the start of a game (freshState() in index.html)
local function freshGame()
  S.day, S.money, S.rep, S.ovens, S.ads, S.supplier, S.loan = 1, 1000, 1, 1, false, 1, 0
  S.staff, S.cands, S.candDay, S.hist = {}, {}, nil, {}
  S.staff = G.startStaff(S, 1, 1)   -- one pizzaiolo and one waiter
  S.shops, S.cur = { { lot = MINE_LOT } }, 1
  S.rival = { name = "Pizza Rápida", q = 52, price = 7, promo = false }
  S.news = { G.news("nw.start") }
  S.contestEntry, S.contestLog, S.lastSales, S.tips, S.studyWeek = nil, {}, {}, {}, -1
  S.over, S.goalDone = false, false
end
local function newId()
  while true do
    local id = "p" .. S.nextId; S.nextId = S.nextId + 1
    local used = false
    for _, p in ipairs(S.menu) do if p.id == id then used = true end end
    if not used then return id end
  end
end
-- each menu pizza keeps its analysis until it changes (p.an = nil)
local function anOf(p) if not p.an then p.an = P.analyze(p) end; return p.an end
-- who picks each menu pizza (G.menuShares), worked out again only when a pizza, its price or its analysis changes
local sharesKey, sharesW
local function shares()
  local k = {}
  for _, p in ipairs(S.menu) do k[#k + 1] = p.id .. ":" .. p.price .. ":" .. tostring(anOf(p)) end
  k = table.concat(k, ",")
  if k ~= sharesKey then sharesKey, sharesW = k, G.menuShares(S, anOf) end
  return sharesW
end
local function copyPieces(ps) local out = {}; for k, x in ipairs(ps) do local c = {}; for kk, vv in pairs(x) do c[kk] = vv end; out[k] = c end; return out end

-- ---------------------------------------------------------------- toppings by group (the pantry tabs)
local catList = {}
local function buildCats()
  for _, c in ipairs(D.CATS) do catList[c] = {} end
  for _, id in ipairs(D.ING_ORDER) do local c = P.ingCat(id); catList[c][#catList[c] + 1] = id end
  local function favIdx(id) for k, f in ipairs(D.FAV) do if f == id then return k end end; return nil end
  for _, c in ipairs(D.CATS) do
    table.sort(catList[c], function(a, b)   -- the classics first, then A to Z in the player's language
      local fa, fb = favIdx(a), favIdx(b)
      if fa or fb then return (fa or 99) < (fb or 99) end
      return P.fold(P.ingName(a)) < P.fold(P.ingName(b))
    end)
  end
end
local function catOf(id) return P.ingCat(id) end
local function idxIn(list, v) for k, x in ipairs(list) do if x == v then return k end end; return 1 end

-- ---------------------------------------------------------------- the pizza being made
local function curCut() return (S.cut == "g" and P.canGrate(S.sel)) and 1 or 0 end
local function curAng() return (S.rot[S.sel] or 0) % P.turns(S.sel) end
local function changed()
  an = P.analyze(S)
  for _, id in ipairs(an.combos) do
    if not P.has(S.found, id) then
      S.found[#S.found + 1] = id
      local q
      for _, c in ipairs(D.COMBOS) do if c.id == id then q = c.q end end
      toast(t(q >= 0 and "k.found" or "k.foundbad", { x = t("combo." .. id) }))
    end
  end
  dirty = true
end

local function addPiece(x, y)
  if math.sqrt(x * x + y * y) > .8 then return false end
  if #S.pieces >= 300 then toast(t("k.full")); return false end
  local mid = P.CENTRED[S.sel] and curCut() == 0
  local lp = S.pieces[#S.pieces]
  if mid and lp and lp.i == S.sel and not lp.g then return false end   -- a drag would pile lobsters up
  if mid then   -- the lobster lands near the middle, at most .25 from it (CENTRE_R in index.html)
    local d = math.sqrt(x * x + y * y)
    if d > .25 then x, y = x * .25 / d, y * .25 / d end
  end
  local piece = { i = S.sel, x = x, y = y, r = math.random() * 6.28, v = math.random(0, 2) }
  if curCut() == 1 then piece.g = 1 elseif P.canRotate(S.sel) then piece.a = curAng() end
  S.pieces[#S.pieces + 1] = piece
  changed()
  return true
end
local function rotatePiece()
  if not P.canRotate(S.sel) then toast(t("k.norotate", { x = P.ingName(S.sel) })); return end
  S.rot[S.sel] = (curAng() + 1) % P.turns(S.sel); dirty = true
end
local function setCut(g)
  if g == 1 and not P.canGrate(S.sel) then toast(t("k.nograte." .. P.noCutKind(S.sel), { x = P.ingName(S.sel) })); return end
  if g == 0 and curCut() == 0 and P.canRotate(S.sel) then rotatePiece(); return end   -- tapping whole again turns the piece
  S.cut = g == 1 and "g" or "w"; dirty = true
end
local function undo()
  if #S.pieces > 0 then S.pieces[#S.pieces] = nil; changed()
  elseif cleared then S.pieces = cleared; cleared = nil; changed() end
end
local function clear()
  if #S.pieces == 0 then return end
  cleared = S.pieces; S.pieces = {}; changed()
end
local function pickTopping(step)
  local list = catList[catOf(S.sel)]
  local k = (idxIn(list, S.sel) - 1 + step) % #list + 1
  if list[k] ~= S.sel then S.cut = "w" end   -- a new topping starts whole
  S.sel = list[k]; dirty = true
end
local function pickCat(step)
  local k = (idxIn(D.CATS, catOf(S.sel)) - 1 + step) % #D.CATS + 1
  S.sel = catList[D.CATS[k]][1]; S.cut = "w"; dirty = true
end
local function cycle(order, cur, step) return order[(idxIn(order, cur) - 1 + step) % #order + 1] end
-- the day and the supplier change every pizza's analysis (topping of the week, supplier's quality and prices)
local function syncWorld()
  P.world.day, P.world.supplier = S.day, S.supplier
  for _, p in ipairs(S.menu) do p.an = nil end
  changed()
end
local function setLang(l)
  P.setLang(l); S.lang = P.lang(); buildCats()
  for _, p in ipairs(S.menu) do p.an = nil end   -- the notes are text in the language
  changed()
end

-- ---------------------------------------------------------------- saving pizzas and the menu
local armed = nil   -- a button pressed once that needs a second press: {what = "new" | "remove", time}
local function arm(what) armed = { what = what, time = 3 } end
local function isArmed(what) return armed and armed.what == what end
local function clampSel() S.msel = math.max(1, math.min(S.msel, #S.menu + 1)) end   -- the row after the last is "+ Create new pizza"
local function freshDraft()
  S.pieces, S.name, S.editing, S.dough, S.sauce = {}, nil, nil, "napo", "tomate"
  cleared = nil; changed()
end
local function newDraft()
  if #S.pieces > 0 and not S.editing and not isArmed("new") then   -- never saved: ask before throwing it away
    arm("new"); toast(t("k.unsaved.title") .. ". " .. t("k.unsaved.new") .. "?"); return
  end
  armed = nil; freshDraft(); S.tab = "kitchen"
end
local function savePizza()
  if #S.pieces < 3 then toast(t("k.needmore")); return end
  local ex
  for k, p in ipairs(S.menu) do if p.id == S.editing then ex = k end end
  local name = S.name
  if not name then   -- no name given: the first combo on it, or "Pizza 4"
    for _, id in ipairs(an.combos) do
      for _, c in ipairs(D.COMBOS) do if c.id == id and c.q > 0 and not name then name = t("combo." .. id) end end
    end
    name = name or ("Pizza " .. (#S.menu + 1))
  end
  local pz = { name = name, dough = S.dough, sauce = S.sauce, pieces = copyPieces(S.pieces) }
  if ex then
    local p = S.menu[ex]
    p.name, p.dough, p.sauce, p.pieces, p.an = pz.name, pz.dough, pz.sauce, pz.pieces, nil
    toast(t("k.updated", { x = name })); S.msel = ex
  else
    pz.id, pz.price = newId(), P.suggestPrice(an.cost)
    S.menu[#S.menu + 1] = pz
    toast(t("k.added", { x = name, p = P.eur(pz.price) })); S.msel = #S.menu
  end
  freshDraft(); S.tab = "menu"   -- saved: the next pizza starts empty, and the Menu shows where it went
end
local function selPizza() return S.menu[S.msel] end
local function editPizza()
  local p = selPizza()
  if not p then newDraft(); return end   -- the "+ Create new pizza" row
  S.dough, S.sauce, S.pieces, S.name, S.editing = p.dough, p.sauce, copyPieces(p.pieces), p.name, p.id
  cleared = nil; S.tab = "kitchen"; changed()
end
local function removePizza()
  local p = selPizza(); if not p then return end
  if not isArmed("remove") then arm("remove"); toast(t("menu.confirm") .. ": " .. p.name .. "?"); return end
  armed = nil
  table.remove(S.menu, S.msel)
  if S.editing == p.id then S.editing = nil end
  clampSel(); dirty = true
end
local function priceStep(d)
  local p = selPizza(); if not p then return end
  p.price = math.max(1, math.min(30, r2(p.price + d))); dirty = true
end
local function pickRow(step) armed = nil; S.msel = S.msel + step; clampSel(); dirty = true end

-- names: the console's keyboard (one textinput with the whole name); on a PC the name is typed in place
local renaming, renameBuf = nil, ""
local function cleanName(s)
  s = s:gsub("[%c|]", ""):gsub("^%s+", ""):gsub("%s+$", "")
  if #s > 40 then s = s:sub(1, 40):gsub("[\192-\255][\128-\191]*$", "") end
  return s
end
local function finishRename(s)
  local set = renaming; renaming = nil
  pcall(love.keyboard.setTextInput, false)
  s = cleanName(s or "")
  if set and s ~= "" then set(s); dirty = true end
end
local function askName(cur, set)
  renaming, renameBuf = set, cur or ""
  if CONSOLE then
    local ok = pcall(love.keyboard.setTextInput, true, { type = "basic", hint = t("k.name"), maxLength = 28 })
    if not ok then pcall(love.keyboard.setTextInput, true) end
  else
    love.keyboard.setTextInput(true)
  end
end
local function renameDraft() askName(S.name or "", function(n) S.name = n end) end
local function renamePizza()
  local p = selPizza(); if not p then return end
  askName(p.name, function(n) p.name = n; if S.editing == p.id then S.name = n end end)
end

-- ---------------------------------------------------------------- drawing helpers
local pages, quads = {}, {}
local fonts = {}
local function hex(h, a)
  local n = tonumber(h:sub(2), 16)
  return { math.floor(n / 65536) / 255, math.floor(n / 256) % 256 / 255, n % 256 / 255, a or 1 }
end
local function col(c, a) love.graphics.setColor(c[1], c[2], c[3], a or c[4] or 1) end
local function spr(key, x, y, alpha, scale)
  local f = A.frames[key]; if not f then return end
  local q = quads[key]
  if not q then q = love.graphics.newQuad(f[2], f[3], f[4], f[5], pages[f[1]]:getDimensions()); quads[key] = q end
  local s = scale or 1
  love.graphics.setColor(1, 1, 1, alpha or 1)
  love.graphics.draw(pages[f[1]], q, math.floor(x - f[4] * s / 2 + .5), math.floor(y - f[5] * s / 2 + .5), 0, s, s)
end
-- icons and bowls: a piece bigger than the box (the whole lobster) is shrunk to fit
local function sprFit(key, x, y, box)
  local f = A.frames[key]; if not f then return end
  spr(key, x, y, nil, math.min(1, box / math.max(f[4], f[5])))
end
--[[ On the 3DS each new font copies the whole system font (about 3 MB), and four of them crashed the console
     while loading. There the game uses only the default font, scaled to each size. On a PC each size is
     its own font (PM3DS_ONEFONT=1 tries the console way). ]]
local ONE_FONT = CONSOLE or (os.getenv and os.getenv("PM3DS_ONEFONT") ~= nil)
local function mkFont(size)
  if ONE_FONT then
    local f = love.graphics.getFont()
    pcall(f.setFilter, f, "linear", "linear")   -- scaled down with "nearest", thin letters (i, l) lost whole columns
    return { f = f, s = size * 1.2 / f:getHeight() }   -- getHeight is the line, about 1.2 times the size
  end
  return { f = love.graphics.newFont(size), s = 1 }
end
local function fw(font, s) local F = fonts[font]; return F.f:getWidth(s) * F.s end   -- width in pixels
local function fprint(font, s, x, y) local F = fonts[font]; love.graphics.setFont(F.f); love.graphics.print(s, x, y, 0, F.s, F.s) end
local function text(s, x, y, font, c, align, w)
  local F = fonts[font]
  love.graphics.setFont(F.f); col(c)
  if align then love.graphics.printf(s, x, y, w / F.s, align, 0, F.s, F.s) else love.graphics.print(s, x, y, 0, F.s, F.s) end
end
local function fitText(s, font, w)   -- cut a line that does not fit, with an ellipsis
  if fw(font, s) <= w then return s end
  while #s > 1 and fw(font, s .. "...") > w do s = s:sub(1, -2):gsub("[\192-\255][\128-\191]*$", "") end
  return s .. "..."
end
local function pxRect(x, y, w, h, c) col(c); love.graphics.rectangle("line", x + .5, y + .5, w - 1, h - 1) end
-- touch buttons: drawn with the bottom screen, and remembered for the next tap
local hits = {}
local function hit(x, y, w, h, fn) hits[#hits + 1] = { x = x, y = y, w = w, h = h, fn = fn } end

local C = {
  ink = hex("#2c1a0b"), bg = hex("#2a170b"), panel = hex("#1a0d05"), cream = hex("#f6e7c8"), gold = hex("#e3b34a"),
  dim = hex("#b39470"), lcd = hex("#8cff73"), good = hex("#8cff73"), bad = hex("#ff7a5c"), combo = hex("#ffd34a"),
}

-- ---------------------------------------------------------------- bottom screen: the bench
local PR = A.pizza / 2
local BW, OY, PX, PY = 320, 22, 12, 37
local PCX, PCY = PX + PR, PY + PR
local BOWLS = { { g = 0, x = 227, y = 26 }, { g = 1, x = 227, y = 94 } }
local BOWL_W, BOWL_H = 58, 40
local LANG_BTN = { x = 272, y = 224, w = 44, h = 14 }

-- big pieces (a lobster, cheese slices) never poke out past the crust: a circular stencil where it works
local function clipCircle(cx, cy, r)
  return pcall(function()
    love.graphics.stencil(function() love.graphics.circle("fill", cx, cy, r) end, "replace", 1)
    love.graphics.setStencilTest("greater", 0)
  end)
end
local function drawPizza(p, cx, cy)
  spr("sauce_" .. p.sauce, cx, cy)
  local clipped = clipCircle(cx, cy, PR - 1)
  for _, x in ipairs(p.pieces) do spr(P.pieceKey(x), cx + x.x * PR, cy + x.y * PR) end   -- in the order they were put
  if clipped then pcall(love.graphics.setStencilTest) end
  spr("crust_" .. p.dough, cx, cy)
end

local function benchLabel(s, x, y, c, hl)
  local w = fw("tiny", s)
  col(hl or { 1, 1, 1, .55 }); fprint("tiny", s, math.floor(x - w / 2), y + 1)
  col(c or C.ink); fprint("tiny", s, math.floor(x - w / 2), y)
end
-- a gold plate button (like the topping's name plate); returns its right edge
local function plateBtn(label, x, y, fn, w, h, danger)
  h = h or 14
  w = w or math.ceil(fw("tiny", label)) + 10
  col(hex("#4a260f")); love.graphics.rectangle("fill", x, y, w, h)
  col(danger and hex("#e0603c") or C.gold); love.graphics.rectangle("fill", x + 1, y + 1, w - 2, h - 2)
  col(danger and hex("#f59a7c") or hex("#fbe39a")); love.graphics.rectangle("fill", x + 1, y + 1, w - 2, 1)
  benchLabel(label, x + w / 2, y + math.floor((h - 10) / 2), hex("#3a2706"), danger and hex("#f59a7c", .8) or hex("#fbe39a", .8))
  hit(x, y, w, h, fn)
  return x + w
end
local function langBtn()
  local L = LANG_BTN
  plateBtn(P.lang() == "pt" and "PT|en" or "EN|pt", L.x, L.y, function() setLang(P.lang() == "pt" and "en" or "pt") end, L.w, L.h)
end
local function nameStrip(name)   -- the pizza's name on the marble strip on top; tap it to rename
  local s = renaming and not CONSOLE and (renameBuf .. "_") or name
  benchLabel(fitText(P.upper(s), "tiny", BW - 8), BW / 2, 6, C.ink, { 1, 1, 1, .4 })
end
local function marble()
  love.graphics.setColor(1, 1, 1)
  spr("marble", BW / 2, 100); spr("marble", BW / 2, 140)
end
local function pizzaOnMarble(p)
  love.graphics.setColor(40 / 255, 30 / 255, 20 / 255, .32)
  love.graphics.ellipse("fill", PCX + 3, PCY + 4, PR + 1, PR)
  drawPizza(p, PCX, PCY)
end

local function drawKitchenBottom()
  marble()
  pizzaOnMarble(S)
  nameStrip(S.name or t("k.newname"))
  hit(0, 0, BW, OY, renameDraft)
  -- right side: name plate and two bowls (whole / chopped)
  local sel, cut = S.sel, curCut()
  love.graphics.push(); love.graphics.translate(0, OY)
  local cx = BOWLS[1].x + BOWL_W / 2
  local label = P.upper(P.ingName(sel))
  local hw = math.min(BW - cx - 3, math.max(46, math.ceil(fw("tiny", label) / 2) + 6))
  col(hex("#4a260f")); love.graphics.rectangle("fill", cx - hw, 6, hw * 2, 13)
  col(C.gold); love.graphics.rectangle("fill", cx - hw + 1, 7, hw * 2 - 2, 11)
  col(hex("#fbe39a")); love.graphics.rectangle("fill", cx - hw + 1, 7, hw * 2 - 2, 1)
  benchLabel(fitText(label, "tiny", hw * 2 - 4), cx, 7, hex("#3a2706"), hex("#fbe39a", .8))
  for _, b in ipairs(BOWLS) do
    local on, ok = b.g == cut, b.g == 0 or P.canGrate(sel)
    local bx, by = b.x + BOWL_W / 2, b.y + 13
    if on then
      pxRect(b.x - 5, b.y - 4, BOWL_W + 10, BOWL_H + 18, hex("#3a2706"))
      pxRect(b.x - 4, b.y - 3, BOWL_W + 8, BOWL_H + 16, C.gold)
      pxRect(b.x - 3, b.y - 2, BOWL_W + 6, BOWL_H + 14, hex("#94661a"))
    end
    spr("bowl", bx, b.y + BOWL_H / 2)
    if ok then
      local f0 = A.frames[sel .. "_0"]
      if b.g == 0 and P.canRotate(sel) then sprFit(P.wholeKey(sel, 0, curAng()), bx, by + 1, 44)
      elseif b.g == 1 and P.BIG_SHRED[sel] then sprFit(sel .. "_g0", bx, by + 2, 46)   -- the big cheese handful
      elseif b.g == 0 and f0 and f0[4] > 36 then sprFit(sel .. "_0", bx, by + 1, 40)   -- one big piece fills the bowl
      else
        local k = b.g == 1 and "_g" or "_"
        spr(sel .. k .. 1, bx - 9, by - 1); spr(sel .. k .. 2, bx + 9, by); spr(sel .. k .. 0, bx, by + 2)
      end
    end
    local key = b.g == 0 and "bench.whole" or (ok and (P.isCheese(sel) and "bench.grated" or "bench.chopped") or "bench.nograte." .. P.noCutKind(sel))
    benchLabel(t(key), bx, b.y + BOWL_H + 3, on and C.ink or hex("#6c5233"))
  end
  -- the little LCD: cost, pieces, weight
  local lx, ly, lw = BOWLS[1].x - 13, 154, BOWL_W + 26
  col(hex("#2a1407")); love.graphics.rectangle("fill", lx - 2, ly - 2, lw + 4, 44)
  col(hex("#081008")); love.graphics.rectangle("fill", lx, ly, lw, 40)
  col(C.lcd)
  local rows = { { "bench.c", P.eur(an.cost) }, { "bench.n", tostring(#S.pieces) }, { "bench.w", P.fmtG(P.pizzaGrams(S)) } }
  for k, r in ipairs(rows) do
    local y = ly + 3 + (k - 1) * 12
    fprint("tiny", t(r[1]), lx + 3, y)
    fprint("tiny", r[2], lx + lw - 3 - fw("tiny", r[2]), y)
  end
  love.graphics.pop()
  -- the strip at the bottom: new pizza, save to the menu, the menu, language
  local x = plateBtn(P.upper(t("k.fresh")), 4, 224, newDraft, nil, nil, isArmed("new"))
  x = plateBtn(P.upper(t(S.editing and "k.save.edit" or "k.save.new")), x + 4, 224, savePizza)
  plateBtn(P.upper(t("nav.menu")), x + 4, 224, function() S.tab = "menu"; clampSel(); dirty = true end)
  langBtn()
end

-- ---------------------------------------------------------------- bottom screen: the chosen menu pizza
local function lcd(x, y, w, rows)
  local h = #rows * 12 + 4
  col(hex("#2a1407")); love.graphics.rectangle("fill", x - 2, y - 2, w + 4, h + 4)
  col(hex("#081008")); love.graphics.rectangle("fill", x, y, w, h)
  for k, r in ipairs(rows) do
    local yy = y + 3 + (k - 1) * 12
    col(C.lcd); fprint("tiny", r[1], x + 3, yy)
    col(r[3] or C.lcd); fprint("tiny", r[2], x + w - 3 - fw("tiny", r[2]), yy)
  end
end
local function drawMenuBottom()
  marble()
  local p = selPizza()
  local strip = function()
    local x = plateBtn(P.upper(t("nav.cozinha")), 4, 224, function() S.tab = "kitchen"; dirty = true end)
    plateBtn(P.upper(t("k.fresh")), x + 4, 224, newDraft, nil, nil, isArmed("new"))
    langBtn()
  end
  if not p then   -- the "+ Create new pizza" row (or an empty menu)
    if #S.menu == 0 then text(t("menu.empty"), 20, 60, "body", C.ink, "center", 280) end
    plateBtn(P.upper(t("menu.new", { n = #S.menu })), 60, 130, newDraft, 200, 24)
    strip(); return
  end
  local a = anOf(p)
  pizzaOnMarble(p)
  nameStrip(p.name)
  hit(0, 0, BW, OY, renamePizza)
  -- right column: price with - and +, the figures, edit / rename / remove
  local rx, rw = 222, 94
  plateBtn("-", rx, 30, function() priceStep(-.5) end, 18, 22)
  plateBtn("+", rx + rw - 18, 30, function() priceStep(.5) end, 18, 22)
  text(P.eur(p.price), rx + 18, 33, "body", C.ink, "center", rw - 36)
  local margin = p.price - a.cost
  lcd(rx, 62, rw, {
    { fitText(P.upper(t("k.q")), "tiny", 60), tostring(a.q), P.qColor(a.q) },
    { t("bench.c"), P.eur(a.cost) },
    { fitText(P.upper(t("menu.margin")), "tiny", 50), P.eur(margin), margin > 0 and C.good or C.bad },
  })
  plateBtn(P.upper(t("menu.edit")), rx, 114, editPizza, rw, 18)
  plateBtn(l3("rename"), rx, 138, renamePizza, rw, 18)
  plateBtn(fitText(P.upper(t(isArmed("remove") and "menu.confirm" or "menu.remove")), "tiny", rw - 6), rx, 162, removePizza, rw, 18, isArmed("remove"))
  -- who picks it: the share of each customer group that would choose this pizza
  text(fitText(t("menu.who"), "tiny", rw), rx, 184, "tiny", C.ink)
  local W, i = shares(), S.msel
  for j, g in ipairs(D.SEG_ORDER) do
    local x, y, v = rx - 2 + ((j - 1) % 2) * 52, 196 + math.floor((j - 1) / 2) * 12, math.floor(W.sh[g][i] * 100 + .5)
    col(hex(D.SEG[g].col), v > 0 and 1 or .4); love.graphics.rectangle("fill", x, y + 3, 6, 6)
    text(t("seg." .. g):sub(1, 3) .. " " .. v .. "%", x + 8, y, "tiny", v > 0 and C.ink or hex("#9a8a70"))
  end
  strip()
end

local drawBottom   -- (defined with the other screens)

-- ---------------------------------------------------------------- top screen: picker and analysis
local function meter(x, y, w, h, v, c)
  col(hex("#000000", .45)); love.graphics.rectangle("fill", x, y, w, h)
  col(c); love.graphics.rectangle("fill", x, y, math.floor(w * v / 100 + .5), h)
end

local drawHeader
-- the screens, in the order SELECT goes through them, and the header that names them
local TABS = { "kitchen", "menu", "day", "contest", "shop", "city" }
local TAB_KEY = { kitchen = "nav.cozinha", menu = "nav.menu", day = "nav.dia", contest = "nav.concurso", shop = "nav.loja", city = "nav.cidade" }
local function goTab(step)
  if anim or report then return end   -- the day runs to its end, and its report is read first
  local k = (idxIn(TABS, S.tab) - 1 + step) % #TABS + 1
  S.tab = TABS[k]; armed = nil; clampSel(); dirty = true
end
local function stars(r) return string.format(P.lang() == "pt" and "%.1f" or "%.1f", r):gsub("%.", P.lang() == "pt" and "," or ".") .. "*" end
drawHeader = function()
  col(C.panel); love.graphics.rectangle("fill", 0, 0, 400, 18)
  local x = 6
  for _, tb in ipairs(TABS) do
    local s = P.upper(t(TAB_KEY[tb]))
    local on = tb == S.tab
    text(s, x, 4, "tiny", on and C.gold or C.dim)
    if on then col(C.gold); love.graphics.rectangle("fill", x, 15, fw("tiny", s), 1) end
    x = x + fw("tiny", s) + 9
  end
  text(P.eur(S.money) .. "   " .. stars(S.rep), 200, 3, "small", S.money < 0 and C.bad or C.cream, "right", 194)
end

local function drawTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  -- left: the topping picker
  local cat = catOf(S.sel)
  local list = catList[cat]
  local k = idxIn(list, S.sel)
  -- the groups as tabs with their symbols (as on phones): L/R change group, the open one is light and raised
  col(C.panel); love.graphics.rectangle("fill", 6, 20, 188, 20)
  text("L", 8, 25, "small", C.dim); text("R", 6, 25, "small", C.dim, "right", 186)
  for i, c in ipairs(D.CATS) do
    local tx = 18 + (i - 1) * 24
    if c == cat then
      col(hex("#f3e6c6")); love.graphics.rectangle("fill", tx, 20, 23, 20)
      pxRect(tx, 20, 23, 20, C.gold)
      spr("cat_" .. c, tx + 11.5, 30)
    else
      col(hex("#7a4520")); love.graphics.rectangle("fill", tx + 1, 23, 21, 16)
      spr("cat_" .. c, tx + 11.5, 31, .7)
    end
  end
  for s = -2, 2 do
    local id = list[(k - 1 + s) % #list + 1]
    local cx, cy = 100 + s * 38, 58
    col(hex(s == 0 and "#4a260f" or "#1a0d05")); love.graphics.rectangle("fill", cx - 17, cy - 17, 34, 34)
    if s == 0 then pxRect(cx - 18, cy - 18, 36, 36, C.gold) end
    sprFit(P.wholeKey(id, 0, 0), cx, cy, 31)
  end
  text(P.ingName(S.sel), 6, 80, "body", C.cream, "center", 188)
  local cutL = curCut() == 1 and t(P.isCheese(S.sel) and "bench.grated" or "bench.chopped") or t("bench.whole")
  text(P.eur(P.ingC(S.sel)) .. " · " .. cutL, 6, 97, "small", C.dim, "center", 188)
  col(C.panel); love.graphics.rectangle("fill", 6, 116, 188, 38)
  text(t("k.dough") .. ":", 10, 120, "small", C.dim); text(t("dough." .. S.dough), 70, 120, "small", C.cream)
  text(t("k.sauce") .. ":", 10, 137, "small", C.dim); text(t("sauce." .. S.sauce), 70, 137, "small", C.cream)
  -- notes
  local y = 160
  if an.n == 0 then
    text(t("k.empty"), 6, y, "small", C.dim, "left", 188)
  else
    for i = 1, math.min(4, #an.notes) do
      local nt = an.notes[i]
      text(fitText(nt[2], "small", 188), 6, y, "small", nt[1] == "good" and C.good or nt[1] == "combo" and C.combo or C.bad)
      y = y + 14
    end
  end
  -- right: quality, cost, appeal
  local rx = 206
  col(C.panel); love.graphics.rectangle("fill", rx - 4, 22, 196, 196)
  local qc = P.qColor(an.q)
  text(t("k.q"), rx, 26, "small", C.dim)
  text(tostring(an.q), rx, 38, "big", qc)
  meter(rx + 52, 48, 130, 8, an.q, qc)
  text(t("k.cost"), rx, 72, "small", C.dim)
  text(P.eur(an.cost), rx, 86, "body", C.cream)
  local nStr = tostring(an.n); if P.lang() == "pt" then nStr = nStr:gsub("%.", ",") end
  text(fitText(t("k.portions", { n = nStr, p = P.eur(P.suggestPrice(an.cost)) }), "small", 186), rx, 104, "small", C.dim)
  text(fitText(t("k.appeal"), "small", 186), rx, 124, "small", C.dim)
  for i, sk in ipairs(D.SEG_ORDER) do
    local yy = 140 + (i - 1) * 18
    text(fitText(t("seg." .. sk), "small", 70), rx, yy, "small", C.cream)
    meter(rx + 74, yy + 3, 88, 8, an.appeal[sk], hex(D.SEG[sk].col))
    text(tostring(an.appeal[sk]), rx + 166, yy, "small", C.cream)
  end
  -- buttons
  text(l3("keys1"), 0, 214, "tiny", C.dim, "center", 400)
  text(l3("keys2"), 0, 226, "tiny", C.dim, "center", 400)
end

-- a menu pizza drawn small (the whole 170 px pizza scaled)
local function miniPizza(p, cx, cy, size)
  love.graphics.push(); love.graphics.translate(cx, cy); love.graphics.scale(size / A.pizza)
  drawPizza(p, 0, 0)
  love.graphics.pop()
end
local ROW_H, ROWS = 34, 5
local function drawMenuTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  local sp = selPizza()
  local loss = sp and sp.price < anOf(sp).cost
  local lead = t("menu.house") .. " (" .. #S.menu .. ")  ·  " .. t("k.book", { n = #S.found, t = #D.COMBOS })
  local why = sp and not loss and G.menuWhy(S, shares(), S.msel)   -- why it is not the first choice of the group it suits best
  if why then text(fitText(why, "tiny", 388), 6, 23, "tiny", C.combo)
  else text(fitText(loss and t("menu.loss", { x = P.eur(anOf(sp).cost - sp.price) }) or lead, "small", 388), 6, 21, "small", loss and C.bad or C.dim) end
  local n = #S.menu + 1
  local first = math.max(1, math.min(S.msel - 2, n - ROWS + 1))
  for row = 0, ROWS - 1 do
    local k = first + row
    if k > n then break end
    local y = 38 + row * ROW_H
    local on = k == S.msel
    col(on and hex("#4a260f") or C.panel); love.graphics.rectangle("fill", 6, y, 388, ROW_H - 3)
    if on then pxRect(5, y - 1, 390, ROW_H - 1, C.gold) end
    local p = S.menu[k]
    if p then
      local a = anOf(p)
      miniPizza(p, 24, y + 15, 28)
      text(fitText(p.name, "body", 200), 44, y + 1, "body", C.cream)
      text(fitText(t("dough." .. p.dough) .. " · " .. t("sauce." .. p.sauce), "tiny", 200), 44, y + 18, "tiny", C.dim)
      text(P.eur(p.price), 250, y + 1, "body", C.gold, "right", 138)
      local margin = p.price - a.cost
      text("Q" .. a.q, 250, y + 18, "tiny", P.qColor(a.q))
      text(t("menu.margin") .. " " .. P.eur(margin), 280, y + 18, "tiny", margin > 0 and C.good or C.bad, "right", 108)
    else
      text(t("menu.new", { n = #S.menu }), 6, y + 8, "body", on and C.gold or C.dim, "center", 388)
    end
  end
  text(l3("mkeys1"), 0, 214, "tiny", C.dim, "center", 400)
  text(l3("nav"), 0, 226, "tiny", C.dim, "center", 400)
end

local function drawToast()
  if toasts[1] then
    local s = toasts[1].s
    local w = math.min(380, fw("body", s) + 16)
    col(hex("#000000", .85)); love.graphics.rectangle("fill", 200 - w / 2, 213, w, 24)
    pxRect(200 - w / 2, 213, w, 24, C.gold)
    text(fitText(s, "body", w - 8), 200 - w / 2, 217, "body", C.combo, "center", w)
  end
end
local drawTopScreen

-- ---------------------------------------------------------------- the day: open the doors, the street, the report
local SEGC = {}
for _, k in ipairs(D.SEG_ORDER) do SEGC[k] = hex(D.SEG[k].col) end
local SALA = require("sala")   -- the dining room on the touch screen (as the browser's day)
local idleScene   -- the room before the doors open: the staff in their places
local function startDay()
  if anim or report then return end
  if #S.menu == 0 then toast(t("ct.need")); return end
  syncWorld(); histOn = false; idleScene = nil
  anim = { res = G.simulateDay(S), t = 0, speed = 1, idx = 1, cnt = { served = 0, rival = 0, left = 0, rev = 0 }, bubbles = {}, sc = SALA.scene(S, G) }
end
local function endDay()
  local a = anim
  anim = nil
  report = G.finishDay(S, a.res)
  syncWorld(); save()
end
local function updateDay(dt)
  local a = anim
  if a.paused then return end
  local k = SALA.pace(a, D.DAY_SECONDS)
  -- small steps, so a fast day does not jump through walls
  local left = math.min(dt, .1) * a.speed * k
  while left > 0 do
    local d = math.min(left, .05); left = left - d
    if SALA.step(a, d, S, D.DAY_SECONDS, P.eur, C) then endDay(); return end
  end
end
local function skipDay()
  if not anim then return end
  while anim.res.events[anim.idx] do anim.idx = anim.idx + 1 end
  endDay()
end

local function lcdRows()
  local a = anim
  local c = a and a.cnt or { served = 0, rival = 0, left = 0, rev = 0 }
  local m = a and math.min(a.t / D.DAY_SECONDS, 1) * 11 * 60 or 0
  local clock = string.format("%02d:%02d", 12 + math.floor(m / 60), math.floor(m % 60 / 15) * 15)
  local share = (c.served + c.rival > 0) and (math.floor(c.served / (c.served + c.rival) * 100 + .5) .. "%") or "--"
  local rep = string.format("%.1f", S.rep); if P.lang() == "pt" then rep = rep:gsub("%.", ",") end
  return {
    { t("lcd.day") .. " " .. S.day .. " " .. P.upper(G.weekday(S.day)), clock },
    { t("lcd.pop"), rep .. "/5" },
    { a and t("lcd.street") or t("lcd.exp"), a and tostring(#a.res.events - a.idx + 1 + #a.sc.people) or ("~" .. G.expected(S)) },
    { t("lcd.served"), tostring(c.served) },
    { t("lcd.rival"), tostring(c.rival) },
    { t("lcd.left"), tostring(c.left) },
    { t("lcd.share"), share },
    false,
    { t("lcd.cooks"), tostring(#G.crew(S, "cook")) },
    { t("lcd.waiters"), tostring(#G.crew(S, "waiter")) },
    { t("lcd.ovens"), tostring(S.ovens) },
    { t("lcd.tables"), D.ROOM.tables .. " · " .. D.ROOM.seats },
    { t("lcd.cap"), c.served .. "/" .. math.min(G.capacity(S), G.serviceCap(S)) },
    false,
    { t("lcd.rev"), P.eur(c.rev) },
    { t("lcd.cash"), P.eur(S.money) },
  }
end
local function drawDayTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  -- the LCD
  col(hex("#2a1407")); love.graphics.rectangle("fill", 4, 22, 196, 178)
  col(hex("#081008")); love.graphics.rectangle("fill", 6, 24, 192, 174)
  local y = 27
  for _, r in ipairs(lcdRows()) do
    if r then
      text(fitText(r[1], "tiny", 130), 10, y, "tiny", C.lcd)
      text(r[2], 10, y, "tiny", C.lcd, "right", 184)
      y = y + 10
    else
      col(C.lcd, .35); love.graphics.rectangle("fill", 10, y + 4, 184, 1); y = y + 9
    end
  end
  -- right: contest today, news, the manager's notes
  local x, w = 206, 190
  y = 22
  if S.day % 5 == 0 then
    local entry
    for _, p in ipairs(S.menu) do if p.id == S.contestEntry then entry = p end end
    local s = "> " .. t("day.ban", { x = P.upper(t("th." .. G.themeFor(S.day))) }) .. " " ..
      (entry and t("day.ban.in", { p = P.upper(entry.name) }) or t("day.ban.none"))
    col(hex("#4a260f")); love.graphics.rectangle("fill", x - 2, y, w + 4, 38)
    text(s, x + 2, y + 2, "tiny", C.combo, "left", w - 4)
    y = y + 42
  end
  text(t("day.news"), x, y, "small", C.gold); y = y + 15
  local notes = {}
  if D.ROOM.seats * 3 < G.expected(S) then notes[#notes + 1] = t("day.seats") end
  if math.min(G.capacity(S), G.serviceCap(S)) < G.expected(S) * .6 then notes[#notes + 1] = t("day.queue") end
  local lines = {}
  for _, n in ipairs(S.news) do lines[#lines + 1] = { G.newsText(n), C.cream } end
  for _, n in ipairs(notes) do table.insert(lines, 1, { t("day.warn") .. ": " .. n, C.bad }) end
  local F = fonts.tiny
  for _, l in ipairs(lines) do
    local _, wrapped = F.f:getWrap(l[1], (w - 4) / F.s)
    local h = #wrapped * F.f:getHeight() * F.s
    if y + h > 200 then break end
    text(l[1], x, y, "tiny", l[2], "left", w - 4)
    y = y + h + 3
  end
  -- who the colours are, centred under both columns
  local lw = 0
  for _, k in ipairs(D.SEG_ORDER) do lw = lw + 20 + fw("tiny", t("seg." .. k)) end
  local lx = math.floor(200 - lw / 2)
  for _, k in ipairs(D.SEG_ORDER) do
    col(SEGC[k]); love.graphics.rectangle("fill", lx, 205, 6, 6)
    local s = t("seg." .. k)
    text(s, lx + 9, 203, "tiny", C.dim)
    lx = lx + 20 + fw("tiny", s)
  end
  text(anim and l3("drun") or (l3("dkeys") .. "   " .. l3("hkeys")), 0, 214, "tiny", C.dim, "center", 400)
  text(l3("nav"), 0, 226, "tiny", C.dim, "center", 400)
end

-- the sales history (as Menu › Sales history in the browser game): totals, profit by day, the last days
local function drawHistTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  local H = S.hist
  text(t("hist.title"), 8, 22, "small", C.gold)
  if #H == 0 then
    text(t("hist.none"), 8, 44, "small", C.cream, "left", 384)
  else
    local served, takings, profit, best = 0, 0, 0, H[1]
    for _, h in ipairs(H) do served = served + h.n; takings = takings + h.v; profit = profit + h.p; if h.p > best.p then best = h end end
    local sum = {
      { t("hist.sum.days"), tostring(#H) }, { t("hist.sum.served"), tostring(served) }, { t("hist.sum.takings"), P.eur(takings) },
      { t("hist.sum.profit"), P.eur(profit) }, { t("hist.sum.avg"), P.eur(profit / #H) }, { t("hist.sum.best"), t("hist.day") .. " " .. best.d .. " · " .. P.eur(best.p) },
    }
    for k, x in ipairs(sum) do
      local cx, cy = 8 + ((k - 1) % 3) * 130, 38 + math.floor((k - 1) / 3) * 22
      text(fitText(x[1], "tiny", 124), cx, cy, "tiny", C.dim); text(fitText(x[2], "small", 124), cx, cy + 9, "small", C.cream)
    end
    -- profit by day: the last 30 days, a bar each, green above the line, red below
    text(t("hist.chart"), 8, 84, "tiny", C.dim)
    local from = math.max(1, #H - 29)
    local mx = 1
    for k = from, #H do mx = math.max(mx, math.abs(H[k].p)) end
    local x0, y0, bw, hh = 8, 126, math.floor(384 / 30), 28
    col(C.dim, .5); love.graphics.rectangle("fill", x0, y0, 384, 1)
    for k = from, #H do
      local h = math.floor(math.abs(H[k].p) / mx * hh + .5)
      col(H[k].p >= 0 and C.good or C.bad)
      love.graphics.rectangle("fill", x0 + (k - from) * bw, H[k].p >= 0 and y0 - h or y0 + 1, bw - 2, h)
    end
    -- how they left, over the kept days (days before the faces have none)
    local tot, any = { 0, 0, 0 }, false
    for _, h in ipairs(H) do if h.f then any = true; for i = 1, 3 do tot[i] = tot[i] + h.f[i] end end end
    if any then
      local all = math.max(1, tot[1] + tot[2] + tot[3])
      local x = 8
      text(t("face.title"), x, 140, "tiny", C.dim); x = x + fw("tiny", t("face.title")) + 10
      for k, key in ipairs({ "good", "meh", "bad" }) do
        SALA.face(key, x + 5, 138)
        local s = math.floor(tot[k] / all * 100 + .5) .. "% " .. t("face." .. key)
        text(s, x + 13, 140, "tiny", C.cream); x = x + 13 + fw("tiny", s) + 12
      end
    end
    -- day by day, the newest first
    local cols = { 8, 60, 120, 190 }
    local y = 162
    for k, s2 in ipairs({ t("hist.day"), t("hist.served"), t("hist.profit"), t("hist.top") }) do text(s2, cols[k], y, "tiny", C.dim) end
    for k = #H, math.max(1, #H - 3), -1 do
      local h = H[k]
      y = y + 11
      text(tostring(h.d), cols[1], y, "tiny", C.cream); text(h.n .. "/" .. h.N, cols[2], y, "tiny", C.cream)
      text(P.eur(h.p), cols[3], y, "tiny", h.p >= 0 and C.good or C.bad)
      text(fitText(h.top ~= "" and (h.top .. " ×" .. h.topN) or "—", "tiny", 200), cols[4], y, "tiny", C.cream)
    end
  end
  text(l3("hback") .. "   " .. l3("nav"), 0, 226, "tiny", C.dim, "center", 400)
end

-- the dining room (sala.lua), the rival's name by the street, and the money bubbles
local function drawRoomBottom()
  if not anim and not idleScene then idleScene = SALA.scene(S, G) end
  SALA.draw(anim, anim and anim.sc or idleScene, S)
  local lbl = P.upper(S.rival.name) .. " >"
  local w = fw("tiny", lbl) + 8
  col(hex("#120a04", .75)); love.graphics.rectangle("fill", 4, 224, w, 13)   -- bottom left: the language button is on the right
  text(lbl, 4, 226, "tiny", hex("#ffcf4a"), "center", w)
  if not anim then return end
  for _, b in ipairs(anim.bubbles) do
    local w = fw("tiny", b.s) + 6
    local x = math.max(2, math.min(318 - w, b.x - w / 2))
    col(hex("#000000", .7)); love.graphics.rectangle("fill", x, b.y, w, 12)
    text(b.s, x, b.y + 1, "tiny", b.c, "center", w)
  end
end
local function drawDayBottom()
  drawRoomBottom()
  if anim then   -- on the back wall, out of the people's way
    local x = 4
    x = plateBtn(P.upper(t(anim.paused and "run.resume" or "run.pause")), x, 2, function() anim.paused = not anim.paused end, nil, 14, anim.paused) + 4
    for _, v in ipairs({ 1, 2, 4 }) do   -- a speed button also resumes
      x = plateBtn("x" .. v, x, 2, function() anim.speed = v; anim.paused = false end, 28, 14, anim.speed == v and not anim.paused) + 4
    end
    plateBtn(P.upper(t("run.skip")), x, 2, skipDay)
  else
    plateBtn(fitText(P.upper(t("day.open", { d = S.day })), "tiny", 300), 20, 196, startDay, 280, 24)
    langBtn()
  end
end

-- the close of the day
local function drawReportTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  local r, res = report, report.res
  text(t("rep.close", { d = r.day, w = G.weekday(r.day) }), 8, 22, "small", C.dim)
  local net = r2(r.profit - (r.interest or 0))   -- the day's result after the bank's interest
  text(t(net >= 0 and "rep.good" or "rep.bad") .. ": " .. P.eur(net), 8, 36, "body", net >= 0 and C.good or C.bad)
  local rows = {
    { t("rep.served"), t("rep.ofN", { n = res.served, N = res.N }) },
    { t("rep.rival", { x = S.rival.name }), tostring(res.toRival) },
    { t("rep.full"), tostring(res.full) },
    { t("rep.noseat"), tostring(res.noseat) },
  }
  local money = {
    { t("rep.revenue"), P.eur(res.revenue) },
    { t("rep.ing"), P.eur(-res.ingCost) },
    { t("rep.rent"), P.eur(-r.rent) },
    { t("rep.sal"), P.eur(-r.sal) },
  }
  if (r.interest or 0) > 0 then money[#money + 1] = { t("rep.interest"), P.eur(-r.interest) } end
  money[#money + 1] = { t("rep.result"), P.eur(net), net >= 0 and C.good or C.bad }
  for k, row in ipairs(rows) do
    local y = 60 + (k - 1) * 15
    text(fitText(row[1], "small", 180 - fw("small", row[2])), 8, y, "small", C.cream); text(row[2], 8, y, "small", C.cream, "right", 186)
  end
  for k, row in ipairs(money) do
    local y = 60 + (k - 1) * (#money > 5 and 13 or 15)
    text(row[1], 208, y, "small", row[3] or C.cream); text(row[2], 208, y, "small", row[3] or C.cream, "right", 186)
  end
  -- how they left: the three faces with their counts, and why the unhappy ones were (as facesHTML() in index.html)
  local fc = { res.happy, res.meh or 0, (res.sad or 0) + res.full + res.noseat + (res.nostock or 0) }
  local x = 8
  text(t("face.title"), x, 142, "tiny", C.dim)
  x = x + fw("tiny", t("face.title")) + 10
  for k, key in ipairs({ "good", "meh", "bad" }) do
    SALA.face(key, x + 5, 140)
    local s = fc[k] .. " " .. t("face." .. key)
    text(s, x + 13, 142, "tiny", C.cream); x = x + 13 + fw("tiny", s) + 12
  end
  if fc[3] > 0 then text(fitText(t("face.why", { f = res.sad or 0, g = fc[3] - (res.sad or 0) }), "tiny", 384), 8, 153, "tiny", C.dim) end
  local f = function(v) local s = string.format("%.2f", v); return P.lang() == "pt" and s:gsub("%.", ",") or s end
  text(t("rep.rep") .. ": " .. f(r.repBefore) .. " -> " .. f(r.repAfter) .. "*", 8, 164, "small", C.gold)
  local w = P.week(S.day)
  local wk = t("wk.ing", { x = P.ingName(w.ing) }) .. "  " .. t("wk.low", { x = P.ingName(w.low) }) .. "  " ..
    t("wk.combo", { x = t("combo." .. w.combo), r = G.comboReq(w.combo) })
  col(hex("#4a260f")); love.graphics.rectangle("fill", 6, 180, 388, 36)
  text(wk, 10, 181, "tiny", C.combo, "left", 380)
  text(l3("rkeys"), 0, 220, "tiny", C.dim, "center", 400)
end
local function closeReport()
  if report and report.res and S.over then report = { over = true }; return end
  report = nil
  if S.over then S.over = false; freshGame(); starterMenu(); S.found = {}; freshDraft(); syncWorld(); S.tab = "kitchen" end
end
local function drawReportBottom()
  col(hex("#f3ead3")); love.graphics.rectangle("fill", 0, 0, 320, 240)
  local r = report
  if r.over then
    text(t("end.title"), 10, 30, "big", C.bad, "center", 300)
    text(t("end.lead", { d = S.day - 1 }), 20, 80, "body", C.ink, "center", 280)
    plateBtn(P.upper(t("end.again")), 60, 180, closeReport, 200, 24)
    return
  end
  local y = 6
  if r.goal then
    text(t("goal.title") .. " " .. t("goal.lead", { m = P.eur(S.money), r = string.format("%.1f", S.rep), d = r.day }), 8, y, "tiny", hex("#1f7a3a"), "left", 304)
    y = y + 34
  end
  -- with several shops: how each did today (the open one first) and the day's total
  if r.others and #r.others > 0 then
    text(t("rep.shops"), 8, y, "tiny", C.ink); text(t("rep.n"), 200, y, "tiny", C.ink, "right", 50); text(t("rep.result"), 250, y, "tiny", C.ink, "right", 60)
    y = y + 11
    local rows = { { name = G.shopName(S), open = true, served = r.res.served, N = r.res.N, profit = r.profit } }
    for _, x in ipairs(r.others) do rows[#rows + 1] = x end
    local tot = 0
    for _, x in ipairs(rows) do
      tot = tot + x.profit
      text(fitText(x.name .. (x.open and "" or (" · " .. t("rep.closed"))), "tiny", 190), 8, y, "tiny", C.ink)
      text(x.open and (x.served .. "/" .. x.N) or "-", 200, y, "tiny", C.ink, "right", 50)
      text(P.eur(x.profit), 250, y, "tiny", x.profit >= 0 and hex("#1f7a3a") or C.bad, "right", 60)
      y = y + 10
    end
    text(t("rep.total"), 8, y, "tiny", C.ink); text(P.eur(r2(tot - (r.interest or 0))), 250, y, "tiny", C.ink, "right", 60)
    y = y + 14
  end
  -- who bought what: each pizza sold, by customer group
  local bs = r.res and r.res.bySeg
  if bs and next(bs) then
    text(t("rep.byseg"), 8, y, "tiny", C.ink)
    for j, g in ipairs(D.SEG_ORDER) do text(t("seg." .. g):sub(1, 3), 160 + (j - 1) * 38, y, "tiny", hex(D.SEG[g].col), "right", 34) end
    y = y + 12
    for _, p in ipairs(S.menu) do
      local any = false
      for _, g in ipairs(D.SEG_ORDER) do if (bs[g] or {})[p.id] then any = true end end
      if any then
        text(fitText(p.name, "tiny", 148), 8, y, "tiny", C.ink)
        for j, g in ipairs(D.SEG_ORDER) do text(tostring((bs[g] or {})[p.id] or 0), 160 + (j - 1) * 38, y, "tiny", C.ink, "right", 34) end
        y = y + 11
      end
    end
    y = y + 4
  end
  local F = fonts.tiny
  for _, q in ipairs(r.quotes) do
    if y > 160 then break end   -- leave room for the contest and the button
    local s = t("seg." .. q[1]) .. ": “" .. q[2] .. "”"
    local _, wrapped = F.f:getWrap(s, 304 / F.s)
    text(s, 8, y, "tiny", C.ink, "left", 304)
    y = y + #wrapped * F.f:getHeight() * F.s + 4
  end
  local c = r.contest
  if c then
    y = y + 2
    text(t("ct.res", { t = t("th." .. c.th), n = c.pos }) .. (c.prize > 0 and (" · +" .. P.eur(c.prize)) or ""), 8, y, "small", hex("#8a5a00")); y = y + 14
    if c.dq then text(t("ct.dq", { x = c.dq }), 8, y, "tiny", C.bad); y = y + 11 end
    for k, x in ipairs(c.rows) do
      local cc = x.me and hex("#8a5a00") or C.ink
      text(k .. ". " .. fitText(x.n, "tiny", 250), 12, y, "tiny", cc); text(tostring(x.s), 12, y, "tiny", cc, "right", 296); y = y + 11
    end
  end
  local res = r.res
  local tip = res.noseat > 3 and "rep.tip.seats" or res.full > 3 and "rep.tip.queue" or res.toRival > res.served and "rep.tip.rival" or nil
  if tip and y < 180 then text(t(tip), 8, math.max(y + 2, 174), "tiny", hex("#6c5233"), "left", 304) end
  plateBtn(P.upper(t("rep.go")), 90, 206, closeReport, 140, 24)
end

-- ---------------------------------------------------------------- the contest
local function enterContest(p)
  if not S.contestEntry then
    if S.money < D.ENTRY_FEE then toast(t("ts.nofee")); return end
    S.money = S.money - D.ENTRY_FEE
  end
  S.contestEntry = p.id; toast(t("ts.entered")); dirty = true
end
local function drawContestTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  local cd = G.nextContestDay(S)
  local th, left = G.themeFor(cd), cd - S.day
  local when = left == 0 and t("ct.today") or left == 1 and t("ct.tomorrow") or t("ct.in", { n = left })
  text(when .. " · " .. t("ct.day", { d = cd }) .. " (" .. G.weekday(cd) .. ")", 8, 22, "small", C.dim)
  text(t("th." .. th), 8, 36, "body", C.gold)
  text(t("th." .. th .. ".d"), 8, 54, "small", C.cream, "left", 384)
  local base = math.floor(math.min(92, 50 + cd * 1.1) + .5)
  local rows = {}
  for k, pr in ipairs({ { 600, .4 }, { 250, .2 }, { 80, .1 } }) do
    local r = tostring(pr[2]); if P.lang() == "pt" then r = r:gsub("%.", ",") end
    rows[#rows + 1] = { t("ct.p" .. k), (t("ct.and", { m = "$" .. pr[1], r = r }):gsub("★", "*")) }
  end
  rows[#rows + 1] = { t("ct.fee"), "$" .. D.ENTRY_FEE }
  rows[#rows + 1] = { t("ct.rivals"), t("ct.pts", { a = base - 8, b = base + 8 }) }
  col(C.panel); love.graphics.rectangle("fill", 6, 88, 192, 80)
  for k, r in ipairs(rows) do
    local y = 91 + (k - 1) * 15
    text(fitText(r[1], "small", 178 - fw("small", r[2])), 10, y, "small", C.dim); text(r[2], 10, y, "small", C.cream, "right", 184)
  end
  col(C.panel); love.graphics.rectangle("fill", 202, 88, 192, 120)
  text(t("ct.hist"), 206, 91, "small", C.gold)
  if #S.contestLog == 0 then text(t("ct.none"), 206, 107, "tiny", C.dim, "left", 184) end
  for k, l in ipairs(S.contestLog) do
    if k > 4 then break end
    local y = 106 + (k - 1) * 25
    text(fitText(t("ct.histrow", { d = l.day, t = t("th." .. l.theme) }), "tiny", 184), 206, y, "tiny", C.cream)
    text(fitText(l.pizza, "tiny", 110), 206, y + 11, "tiny", C.dim)
    text(t("ct.place", { n = l.pos }) .. (l.prize > 0 and (" · " .. P.eur(l.prize)) or ""), 206, y + 11, "tiny", C.combo, "right", 184)
  end
  text(t("ct.judge", { d = cd }), 8, 174, "tiny", C.dim, "left", 190)
  text(l3("ckeys"), 0, 214, "tiny", C.dim, "center", 400)
  text(l3("nav"), 0, 226, "tiny", C.dim, "center", 400)
end
local function drawContestBottom()
  col(hex("#f3ead3")); love.graphics.rectangle("fill", 0, 0, 320, 240)
  text(t("ct.pick"), 8, 4, "small", C.ink)
  text(fitText(t(S.contestEntry and "ct.swap" or "ct.pay"), "tiny", 304), 8, 19, "tiny", hex("#6c5233"))
  if #S.menu == 0 then text(t("ct.need"), 8, 60, "body", C.ink, "center", 304); langBtn(); return end
  S.csel = math.max(1, math.min(S.csel, #S.menu))
  local th = G.themeFor(G.nextContestDay(S))
  local RH, N = 30, 6
  local first = math.max(1, math.min(S.csel - 2, #S.menu - N + 1))
  for row = 0, N - 1 do
    local k = first + row
    local p = S.menu[k]
    if not p then break end
    local y = 34 + row * RH
    local on, entered = k == S.csel, p.id == S.contestEntry
    col(entered and hex("#e3b34a") or on and hex("#eadcb8") or hex("#f9f3e3")); love.graphics.rectangle("fill", 6, y, 308, RH - 3)
    if on then pxRect(5, y - 1, 310, RH - 1, hex("#4a260f")) end
    miniPizza(p, 22, y + 13, 24)
    local sc = P.contestScore(th, p)
    text(fitText((entered and "> " or "") .. p.name, "small", 170), 40, y + 2, "small", C.ink)
    text(sc.dq and t("ct.dq", { x = sc.dq }) or t("ct.pre", { n = math.floor(sc.s + .5) }), 40, y + 15, "tiny", sc.dq and hex("#b0381c") or hex("#6c5233"))
    hit(6, y, 308, RH - 3, function() S.csel = k; enterContest(p) end)
  end
  langBtn()
end

-- ---------------------------------------------------------------- the shop
local SHOP_ROWS = { "oven", "team", "hire", "ads", "supplier", "study", "bank", "reset" }
local function shopItem(id) for _, it in ipairs(G.SHOP) do if it.id == id then return it end end end
local function buyItem(it)
  if not it.ok(S) then return end
  local c = it.cost(S)
  if S.money < c then return end
  S.money = S.money - c; it.buy(S); toast(t("ts.bought", { x = t("shop." .. it.id) })); dirty = true
end
local function setSupplier(k) S.supplier = k; syncWorld() end
local function runStudy()
  if S.studyWeek == G.weekOf(S.day) or S.money < D.STUDY_COST then return end
  S.money = S.money - D.STUDY_COST; S.studyWeek = G.weekOf(S.day)
  table.insert(S.tips, 1, G.studyTips(S))
  while #S.tips > 6 do table.remove(S.tips) end
  dirty = true
end
local function resetGame()
  if not isArmed("reset") then arm("reset"); toast(t("ts.sure")); return end
  armed = nil
  freshGame(); starterMenu(); S.found = {}; freshDraft(); syncWorld(); S.tab = "kitchen"
  toast(t("ts.reset"))
end
local function shopAction(id)
  local it = shopItem(id)
  if it then buyItem(it)
  elseif id == "supplier" then setSupplier(S.supplier % 3 + 1)
  elseif id == "study" then runStudy()
  elseif id == "reset" then resetGame() end
end
local function shopRow(id)   -- name, state, price
  local it = shopItem(id)
  if it then return t("shop." .. id), it.lvl(S), it.ok(S) and P.eur(it.cost(S)) or t("shop.done") end
  if id == "supplier" then return t("sup.title"), t("sup." .. S.supplier), "" end
  if id == "study" then return t("study.title"), S.studyWeek == G.weekOf(S.day) and t("study.done") or "", P.eur(D.STUDY_COST) end
  if id == "team" then return t("staff.title"), t("staff.pay", { w = P.eur(G.wages(S)) }), "" end
  if id == "hire" then return t("staff.cands"), "", P.eur(D.HIRE_COST) end
  if id == "bank" then return t("bank.title"), t("bank.owe") .. " " .. P.eur(S.loan or 0), "" end
  return t("shop.reset"), "", ""
end
local function drawShopTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  text(fitText(t("shop.lead", { m = P.eur(S.money) }), "small", 388), 6, 21, "small", C.dim)
  S.ssel = math.max(1, math.min(S.ssel, #SHOP_ROWS))
  for k, id in ipairs(SHOP_ROWS) do
    local y = 38 + (k - 1) * 21
    local on = k == S.ssel
    col(on and hex("#4a260f") or C.panel); love.graphics.rectangle("fill", 6, y, 388, 19)
    if on then pxRect(5, y - 1, 390, 21, C.gold) end
    local n, l, c = shopRow(id)
    text(fitText(n, "small", 166), 12, y + 3, "small", id == "reset" and C.bad or C.cream)
    text(fitText(l, "tiny", 150), 180, y + 4, "tiny", C.dim)
    text(c, 12, y + 3, "small", C.gold, "right", 376)
  end
  text(l3("skeys"), 0, 214, "tiny", C.dim, "center", 400)
  text(l3("nav"), 0, 226, "tiny", C.dim, "center", 400)
end
local function drawShopBottom()
  col(hex("#f3ead3")); love.graphics.rectangle("fill", 0, 0, 320, 240)
  local id = SHOP_ROWS[S.ssel]
  local it = shopItem(id)
  local n = shopRow(id)
  text(n, 10, 6, "body", C.ink)
  local brown = hex("#6c5233")
  if it then
    text(it.d(), 10, 28, "small", brown, "left", 300)
    text(it.lvl(S), 10, 70, "small", C.ink)
    local ok = it.ok(S)
    local lbl = ok and (P.upper(t("shop.buy")) .. "  " .. P.eur(it.cost(S))) or P.upper(t("shop.done"))
    plateBtn(lbl, 10, 96, function() buyItem(it) end, 150, 24, ok and S.money < it.cost(S))
  elseif id == "team" then
    -- the team, two lines a person: name, role and wage; speed and the second skill (cooking or charm) as n/5
    local y = 26
    for _, p in ipairs(S.staff) do
      text(fitText(p.n .. " · " .. t("staff." .. p.r) .. " · " .. t("staff.wage", { w = P.eur(p.w) }), "tiny", 230), 10, y, "tiny", C.ink)
      text(t("staff.sp") .. " " .. p.sp .. "/5 · " .. t("staff.sk." .. p.r) .. " " .. p.sk .. "/5", 10, y + 10, "tiny", brown)
      if #G.crew(S, p.r) > 1 then
        local who = p
        plateBtn(P.upper(t("staff.fire")), 246, y + 2, function() local x = G.letGo(S, who.id); if x then toast(t("ts.fired2", { x = x.n })); dirty = true end end, 64, 16)
      end
      y = y + 22
    end
  elseif id == "hire" then
    local day = S.candDay
    local cands = G.candidates(S)
    if day ~= S.candDay then dirty = true end   -- a new day brought new people
    text(t("staff.candlead", { c = P.eur(D.HIRE_COST) }), 10, 26, "tiny", brown, "left", 300)
    local y = 52
    if #cands == 0 then text(t("staff.none"), 10, y, "small", C.ink, "left", 300) end
    for _, p in ipairs(cands) do
      text(fitText(p.n .. " · " .. t("staff." .. p.r) .. " · " .. t("staff.wage", { w = P.eur(p.w) }), "tiny", 222), 10, y, "tiny", C.ink)
      text(t("staff.sp") .. " " .. p.sp .. "/5 · " .. t("staff.sk." .. p.r) .. " " .. p.sk .. "/5", 10, y + 10, "tiny", brown)
      local full, who = #G.crew(S, p.r) >= D.MAX_STAFF[p.r], p
      plateBtn(P.upper(t(full and "staff.full" or "staff.hire")), 238, y + 2, function()
        if full then return end
        local x = G.hire(S, who.id); if x then toast(t("ts.hired", { x = x.n })); dirty = true end
      end, 72, 16, not full and S.money < D.HIRE_COST)
      y = y + 25
    end
  elseif id == "bank" then
    local owe = S.loan or 0
    text(t("bank.lead", { r = (P.lang() == "pt" and "0,5" or "0.5") }), 10, 26, "tiny", brown, "left", 300)
    local rows = { { t("bank.owe"), P.eur(owe) }, { t("bank.today"), P.eur(owe * D.BANK_RATE) }, { t("bank.limit"), P.eur(D.BANK_MAX) } }
    for k, r in ipairs(rows) do
      text(r[1], 10, 52 + (k - 1) * 14, "small", C.ink); text(r[2], 10, 52 + (k - 1) * 14, "small", C.ink, "right", 300)
    end
    local x = 10
    for _, v in ipairs({ 500, 2000, 5000 }) do
      local amt = v
      x = plateBtn(P.upper(t("bank.borrow", { x = P.eur(v):gsub("%.00$", "") })), x, 100, function()
        if G.borrow(S, amt) then toast(t("bank.got", { x = P.eur(amt):gsub("%.00$", "") })); dirty = true
        else toast(t("bank.max", { x = P.eur(D.BANK_MAX):gsub("%.00$", "") })) end
      end, 96, 20) + 6
    end
    local function pay(v) local x = G.repay(S, v); if x then toast(t("bank.paid", { x = P.eur(x) })); dirty = true end end
    plateBtn(P.upper(t("bank.repay", { x = "$500" })), 10, 128, function() pay(500) end, 140, 20, owe > 0 and S.money < math.min(500, owe))
    plateBtn(P.upper(t("bank.all")), 160, 128, function() pay(nil) end, 140, 20, owe > 0 and S.money < owe)
  elseif id == "supplier" then
    text(t("sup.lead"), 10, 28, "tiny", brown, "left", 300)
    for k = 1, 3 do
      local y = 74 + (k - 1) * 40
      local sp = D.SUPPLIER[k]
      plateBtn(P.upper(t("sup." .. k)), 10, y, function() setSupplier(k) end, 130, 30, S.supplier == k)
      text(k == 1 and t("sup.d1") or t("sup.d", { q = sp.q, m = math.floor((sp.m - 1) * 100 + .5) }), 148, y + 2, "tiny", brown, "left", 162)
    end
  elseif id == "study" then
    text(t("study.lead"), 10, 28, "tiny", brown, "left", 300)
    local done = S.studyWeek == G.weekOf(S.day)
    plateBtn(done and P.upper(t("study.done")) or (P.upper(t("study.btn")) .. "  " .. P.eur(D.STUDY_COST)), 10, 76, runStudy, 200, 24)
    local y = 108
    for _, x in ipairs(S.tips) do
      for _, line in ipairs(G.tipText(x)) do
        if y > 210 then break end
        text("- " .. line, 10, y, "tiny", C.ink, "left", 300)
        local _, wr = fonts.tiny.f:getWrap("- " .. line, 300 / fonts.tiny.s)
        y = y + #wr * fonts.tiny.f:getHeight() * fonts.tiny.s + 2
      end
    end
  else
    plateBtn(P.upper(isArmed("reset") and t("ts.sure") or t("shop.reset")), 10, 40, resetGame, 300, 24, true)
  end
  langBtn()
end

-- ---------------------------------------------------------------- the city
--[[ Porto Magno (city.js): the streets and houses on top (gfx/city.png, painted by tools/export_3ds_city.js, 904x704),
     and on the touch screen a navigator (the whole town small, gfx/city_mini.png) next to the chosen building. Touch
     or drag on the navigator to look somewhere, or use the D-pad to jump to the next building worth seeing in that
     direction (to rent, for sale, a rival, your shops, the landmarks); A rents, buys or goes to your shop (press
     twice), Y closes or sells it, X zooms in. ]]
local CL = D.CITY.LOTS
local cityImg, cityMini
local city = { sel = nil, z = 1, armed = nil, cam = nil, drag = false }
local CITY_MINI_W, MINI_X, MINI_Y = 152, 4, 4   -- the navigator (as made by tools/export_3ds_city.js)
local CITY_MINI_H = math.floor(CITY_MINI_W * D.CITY.LH / D.CITY.LW + .5)
local MINI_K = CITY_MINI_W / D.CITY.LW
local CITY_TOP = 18   -- below the header
local function cityShown(i) local k = G.lotKind(S, i); return k == "rent" or k == "sale" or k == "rival" or k == "mine" or k == "land" end
local function cityPick(dx, dy)   -- the nearest building worth seeing in that direction
  local a = CL[city.sel]
  local ax, ay = a.x + a.w / 2, a.y + a.h / 2
  local best, bs
  for i, l in ipairs(CL) do
    if i ~= city.sel and cityShown(i) then
      local x, y = l.x + l.w / 2 - ax, l.y + l.h / 2 - ay
      local along, across = x * dx + y * dy, math.abs(x * dy - y * dx)
      if along > 4 then
        local sc = along + across * 2
        if not bs or sc < bs then best, bs = i, sc end
      end
    end
  end
  if best then city.sel, city.armed = best, nil end
end
local function cityPickAt(mx, my)   -- the building worth seeing nearest to a point of the map
  local best, bd
  for i, l in ipairs(CL) do
    if cityShown(i) then
      local d = (l.x + l.w / 2 - mx) ^ 2 + (l.y + l.h / 2 - my) ^ 2
      if not bd or d < bd then best, bd = i, d end
    end
  end
  if best and best ~= city.sel then city.sel, city.armed = best, nil end
end
local function inMini(x, y) return x >= MINI_X and x < MINI_X + CITY_MINI_W and y >= MINI_Y and y < MINI_Y + CITY_MINI_H end
local function cityTouch(x, y) cityPickAt((x - MINI_X) / MINI_K, (y - MINI_Y) / MINI_K) end
local function cityAct(close)   -- A: rent / buy / go to the shop; Y: close or sell your shop (each pressed twice)
  local i = city.sel
  local k = G.lotKind(S, i)
  if close then
    if k ~= "mine" or #S.shops < 2 then return end
    if city.armed ~= "c" .. i then city.armed = "c" .. i; toast(t("city.sure")); return end
    city.armed = nil
    local name, gain = G.closeShop(S, G.lotShop(S, i))
    if name then toast(gain > 0 and t("city.sold", { x = name, p = P.eur(gain):gsub("%.00$", "") }) or t("city.closed", { x = name })); syncWorld(); dirty = true end
    return
  end
  if k == "mine" then
    local own = G.lotShop(S, i)
    if own ~= S.cur and G.openShop(S, own) then clampSel(); syncWorld(); dirty = true; toast(t("shop.now", { x = G.shopName(S) })) end
  elseif k == "rent" or k == "sale" then
    if G.ownMoney(S) < D.CITY_CASH then toast(t("city.need", { m = P.eur(D.CITY_CASH):gsub("%.00$", "") })); return end
    if city.armed ~= i then city.armed = i; toast(t("city.sure")); return end
    city.armed = nil
    local ok, why = G.openLot(S, i, k == "sale")
    if ok then clampSel(); syncWorld(); dirty = true; toast(t("city.open.t", { x = G.shopName(S) }))
    elseif why then toast(t(why, { m = P.eur(D.CITY_CASH):gsub("%.00$", "") })) end
  end
end
local function drawCityTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  if not cityImg then cityImg = love.graphics.newImage("gfx/city.png") end
  city.sel = city.sel or S.shops[S.cur].lot
  local z, l = city.z, CL[city.sel]
  local vw, vh = 400 / z, (240 - CITY_TOP - 22) / z
  local cx = math.max(0, math.min(D.CITY.LW - vw, l.x + l.w / 2 - vw / 2))
  local cy = math.max(0, math.min(D.CITY.LH - vh, l.y + l.h / 2 - vh / 2))
  if vw > D.CITY.LW then cx = (D.CITY.LW - vw) / 2 end
  city.cam = { x = cx, y = cy, w = vw, h = vh }   -- shown as a frame on the navigator
  local function P2(x, y) return math.floor((x - cx) * z), math.floor((y - cy) * z) + CITY_TOP end
  love.graphics.setScissor(0, CITY_TOP, 400, 240 - CITY_TOP - 22)
  local ix, iy = P2(0, 0)
  col({ 1, 1, 1 }); love.graphics.draw(cityImg, ix, iy, 0, z, z)
  -- signs and pins: to rent / for sale, rivals, your shops (* the one open), the landmarks
  for i, x in ipairs(CL) do
    local k = G.lotKind(S, i)
    local px, py = P2(x.x + x.w / 2, x.y + x.h / 2)
    if k == "rent" or k == "sale" or k == "rival" or k == "mine" or k == "land" then
      local s2 = k == "land" and P.upper(t("land." .. x.land)) or k == "rent" and t("city.sign.rent") or k == "sale" and t("city.sign.sale")
        or k == "rival" and t("city.pin.rival") or (t("city.pin.mine") .. (G.lotShop(S, i) == S.cur and " *" or ""))
      local c = hex(D.CITY.KCOL[k] or "#2a1407")
      do
        local w = fw("tiny", s2) + 6
        col(hex("#120a04")); love.graphics.rectangle("fill", px - w / 2 - 1, py - 7, w + 2, 13)
        col(k == "land" and hex("#2a1407", .85) or c); love.graphics.rectangle("fill", px - w / 2, py - 6, w, 11)
        text(s2, px - w / 2, py - 6, "tiny", k == "land" and C.combo or hex("#ffffff"), "center", w)
      end
    end
  end
  local x0, y0 = P2(l.x, l.y)
  col(hex("#120a04")); love.graphics.setLineWidth(3); love.graphics.rectangle("line", x0, y0, l.w * z, l.h * z)
  col(C.combo); love.graphics.setLineWidth(1); love.graphics.rectangle("line", x0 + .5, y0 + .5, l.w * z - 1, l.h * z - 1)
  love.graphics.setScissor()
  drawHeader()
  text(l3("citykeys"), 0, 220, "tiny", C.dim, "center", 400)
  text(l3("nav"), 0, 230, "tiny", C.dim, "center", 400)
end
local function drawCityBottom()
  col(hex("#f3ead3")); love.graphics.rectangle("fill", 0, 0, 320, 240)
  if not cityMini then cityMini = love.graphics.newImage("gfx/city_mini.png") end
  city.sel = city.sel or S.shops[S.cur].lot
  local i = city.sel
  local l, k = CL[i], G.lotKind(S, i)
  local own = G.lotShop(S, i)
  local brown = hex("#6c5233")
  -- the navigator: the whole town, a dot on each building worth seeing, the top screen's view as a frame
  col(hex("#120a04")); love.graphics.rectangle("fill", MINI_X - 2, MINI_Y - 2, CITY_MINI_W + 4, CITY_MINI_H + 4)
  col({ 1, 1, 1 }); love.graphics.draw(cityMini, MINI_X, MINI_Y)
  for j, x in ipairs(CL) do
    local kk = G.lotKind(S, j)
    if kk == "rent" or kk == "sale" or kk == "rival" or kk == "mine" then
      local px, py = MINI_X + (x.x + x.w / 2) * MINI_K, MINI_Y + (x.y + x.h / 2) * MINI_K
      col(hex("#120a04")); love.graphics.rectangle("fill", math.floor(px) - 2, math.floor(py) - 2, 5, 5)
      col(hex(D.CITY.KCOL[kk])); love.graphics.rectangle("fill", math.floor(px) - 1, math.floor(py) - 1, 3, 3)
    end
  end
  if city.cam then
    local c = city.cam
    local fx, fy = math.floor(MINI_X + c.x * MINI_K), math.floor(MINI_Y + c.y * MINI_K)   -- the camera stays inside the map
    local fw2, fh2 = math.floor(c.w * MINI_K), math.floor(c.h * MINI_K)
    col(hex("#120a04")); love.graphics.rectangle("line", fx - .5, fy - .5, fw2 + 1, fh2 + 1)
    col(C.combo); love.graphics.rectangle("line", fx + .5, fy + .5, fw2 - 1, fh2 - 1)
  end
  -- the building
  local RX, RW = 164, 150
  local title = k == "land" and t("land." .. l.land) or k == "rival" and l.name or k == "mine" and G.shopName(S, own)
    or k == "taken" and t("biz." .. l.biz) or l.addr
  local chip = t("city.k." .. k)
  local cw = fw("tiny", chip) + 8
  col(hex(D.CITY.KCOL[k] or "#7a6a55")); love.graphics.rectangle("fill", RX, 3, cw, 12)
  text(chip, RX, 4, "tiny", hex("#ffffff"), "center", cw)
  text(t("hood." .. l.hood), RX + cw + 6, 4, "tiny", brown)
  local F = fonts.tiny
  local function wrapped(str, y, c)   -- a paragraph in the right column; returns the next y
    local _, lines = F.f:getWrap(str, RW / F.s)
    text(str, RX, y, "tiny", c or brown, "left", RW)
    return y + #lines * F.f:getHeight() * F.s + 2
  end
  local y = wrapped(title, 18, C.ink) + 2
  local function row(a2, b2) text(a2, RX, y, "tiny", C.ink); text(b2, RX, y, "tiny", C.ink, "right", RW); y = y + 11 end
  if k == "land" then
    y = wrapped(t("land.d." .. l.land), y)
    if l.land == "square" then y = wrapped(t("city.contest"), y + 2) end
  else
    if title ~= l.addr then y = wrapped(l.addr, y) end
    if k == "rival" then
      y = wrapped(t("rv.style") .. ": " .. t("rv." .. (l.name == "Pizza Rápida" and "classic" or D.HOOD_STYLE[l.hood])), y)
    else
      row(t("city.traffic"), l.traffic .. "/5")
      if k == "rent" or k == "sale" then
        row(t("city.cond"), t("city.c." .. l.cond) .. (l.cond == "works" and (" · " .. P.eur(l.works):gsub("%.00$", "")) or ""))
      end
      if k == "sale" then row(t("city.price"), (P.eur(l.price):gsub("%.00$", "")))
      elseif k ~= "taken" then row(t("city.rent"), P.eur(own and G.rentOf(S, own) or l.rent):gsub("%.00$", "") .. t("city.perday")) end
    end
  end
  -- who comes in this neighbourhood, under the navigator
  y = MINI_Y + CITY_MINI_H + 6
  text(t("city.mix"), 10, y, "tiny", C.ink); y = y + 11
  local mix, bx = D.CITY.HOODS[l.hood].mix, 10
  for j, g in ipairs(D.SEG_ORDER) do
    local w = math.floor(mix[j] / 100 * 300 + .5)
    col(hex(D.SEG[g].col)); love.graphics.rectangle("fill", bx, y, w, 8); bx = bx + w
  end
  y = y + 10
  local lx = 10
  for j, g in ipairs(D.SEG_ORDER) do
    local s2 = t("seg." .. g) .. " " .. mix[j] .. "%"
    text(s2, lx, y, "tiny", hex(D.SEG[g].col)); lx = lx + fw("tiny", s2) + 8
  end
  y = y + 15
  -- what you can do here
  if k == "rent" or k == "sale" then
    local buy = k == "sale"
    local can = G.ownMoney(S) >= D.CITY_CASH
    local lbl = city.armed == i and t("city.sure") or buy and (t("city.bBuy") .. " · " .. P.eur(G.lotCost(l, true)):gsub("%.00$", ""))
      or (t("city.bRent") .. " · " .. P.eur(l.rent):gsub("%.00$", "") .. t("city.perday"))
    plateBtn(P.upper(lbl), 10, y, function() cityAct(false) end, 300, 20, not can)
    y = y + 23
    local w = l.cond == "works" and P.eur(l.works):gsub("%.00$", "") or "$0"
    text(can and (buy and t("city.cost.buy", { p = P.eur(l.price):gsub("%.00$", ""), w = w }) or t("city.cost.rent", { w = w, r = P.eur(l.rent):gsub("%.00$", "") }))
      or t("city.need", { m = P.eur(D.CITY_CASH):gsub("%.00$", "") }), 10, y, "tiny", brown, "left", 300)
  elseif k == "mine" then
    if own == S.cur then text(t("city.here"), 10, y + 4, "small", hex("#8a5a00"))
    else plateBtn(P.upper(t("city.go")), 10, y, function() cityAct(false) end, 145, 20) end
    if #S.shops > 1 then
      local sh = S.shops[own]
      local lbl = city.armed == "c" .. i and t("city.sure") or sh.owned and t("city.sell", { x = P.eur(math.floor(l.price * D.SELL_SHARE + .5)):gsub("%.00$", "") }) or t("city.close")
      plateBtn(P.upper(fitText(lbl, "tiny", 135)), 165, y, function() cityAct(true) end, 145, 20, true)
    end
  end
  text(t("city.yours") .. ": " .. #S.shops, 10, 226, "tiny", brown)
  langBtn()
end

drawBottom = function()
  hits = {}
  if report then drawReportBottom()
  elseif S.tab == "menu" then drawMenuBottom()
  elseif S.tab == "day" then drawDayBottom()
  elseif S.tab == "contest" then drawContestBottom()
  elseif S.tab == "shop" then drawShopBottom()
  elseif S.tab == "city" then drawCityBottom()
  else drawKitchenBottom() end
end
drawTopScreen = function()
  if report then drawReportTop()
  elseif S.tab == "menu" then drawMenuTop()
  elseif S.tab == "day" and histOn and not anim then drawHistTop()
  elseif S.tab == "day" then drawDayTop()
  elseif S.tab == "contest" then drawContestTop()
  elseif S.tab == "shop" then drawShopTop()
  elseif S.tab == "city" then drawCityTop()
  else drawTop() end
  drawToast()
end

-- ---------------------------------------------------------------- input
local drag = nil
local function benchPoint(x, y) return (x - PCX) / PR, (y - PCY) / PR end
local function touchDown(x, y)
  if renaming and not CONSOLE then finishRename(renameBuf) end   -- PC: a tap elsewhere keeps what was typed
  if S.tab == "city" and not report and inMini(x, y) then city.drag = true; cityTouch(x, y); return end
  for k = #hits, 1, -1 do
    local h = hits[k]
    if x >= h.x and x < h.x + h.w and y >= h.y and y < h.y + h.h then h.fn(); return end
  end
  if S.tab ~= "kitchen" then return end
  for _, b in ipairs(BOWLS) do
    if x >= b.x - 6 and x <= b.x + BOWL_W + 6 and y - OY >= b.y - 4 and y - OY <= b.y + BOWL_H + 16 then setCut(b.g); return end
  end
  local px, py = benchPoint(x, y)
  if math.sqrt(px * px + py * py) > 1 then return end
  drag = { x = 9, y = 9 }
  if addPiece(px, py) then drag = { x = px, y = py } end
end
local function touchMove(x, y)
  if city.drag then if inMini(x, y) then cityTouch(x, y) end; return end
  if not drag then return end
  local px, py = benchPoint(x, y)
  if math.sqrt((px - drag.x) ^ 2 + (py - drag.y) ^ 2) > .2 and addPiece(px, py) then drag = { x = px, y = py } end
end
local function touchUp() drag = nil; city.drag = false end

local held = {}
local function navButton(b)   -- outside the Kitchen: L/R and SELECT go through the screens, START quits
  if b == "leftshoulder" then goTab(-1)
  elseif b == "rightshoulder" or b == "back" then goTab(1)
  elseif b == "start" then save(); love.event.quit() end
end
local function otherButton(b)
  if report then if b == "a" then closeReport() end; return end
  if S.tab == "day" then
    if anim then
      if b == "a" then skipDay()
      elseif b == "b" then anim.paused = not anim.paused   -- the clock stops; the room is still drawn
      elseif b == "dpleft" then anim.speed = math.max(1, anim.speed / 2); anim.paused = false
      elseif b == "dpright" then anim.speed = math.min(4, anim.speed * 2); anim.paused = false end
    elseif b == "a" then startDay()
    elseif b == "y" then histOn = not histOn
    else navButton(b) end
  elseif S.tab == "contest" then
    if b == "dpup" then S.csel = math.max(1, S.csel - 1)
    elseif b == "dpdown" then S.csel = math.min(#S.menu, S.csel + 1)
    elseif b == "a" and S.menu[S.csel] then enterContest(S.menu[S.csel])
    else navButton(b) end
  elseif S.tab == "city" then
    city.sel = city.sel or S.shops[S.cur].lot
    if b == "dpleft" then cityPick(-1, 0) elseif b == "dpright" then cityPick(1, 0)
    elseif b == "dpup" then cityPick(0, -1) elseif b == "dpdown" then cityPick(0, 1)
    elseif b == "a" then cityAct(false)
    elseif b == "y" then cityAct(true)
    elseif b == "x" then city.z = city.z == 1 and 2 or 1
    else navButton(b) end
  elseif S.tab == "shop" then
    if b == "dpup" then S.ssel = math.max(1, S.ssel - 1); armed = nil
    elseif b == "dpdown" then S.ssel = math.min(#SHOP_ROWS, S.ssel + 1); armed = nil
    elseif b == "a" then shopAction(SHOP_ROWS[S.ssel])
    else navButton(b) end
  end
end
local function menuButton(b)
  if b == "dpup" then pickRow(-1)
  elseif b == "dpdown" then pickRow(1)
  elseif b == "dpleft" then priceStep(-.5)
  elseif b == "dpright" then priceStep(.5)
  elseif b == "a" then editPizza()
  elseif b == "x" then renamePizza()
  elseif b == "y" then removePizza()
  else navButton(b) end
end
local function button(b)
  if report or S.tab == "day" or S.tab == "contest" or S.tab == "shop" or S.tab == "city" then otherButton(b); return end
  if S.tab == "menu" then menuButton(b); return end
  if b == "dpleft" then pickTopping(-1)
  elseif b == "dpright" then pickTopping(1)
  elseif b == "leftshoulder" then pickCat(-1)
  elseif b == "rightshoulder" then pickCat(1)
  elseif b == "dpup" then S.dough = cycle(D.DOUGH_ORDER, S.dough, 1); changed()
  elseif b == "dpdown" then S.sauce = cycle(D.SAUCE_ORDER, S.sauce, 1); changed()
  elseif b == "a" then setCut(1 - curCut())
  elseif b == "x" then rotatePiece()
  elseif b == "b" then undo()
  elseif b == "y" then clear()
  elseif b == "back" then goTab(1)
  elseif b == "start" then save(); love.event.quit() end
end
local REPEAT = { dpleft = true, dpright = true, dpup = true, dpdown = true }
local function press(b) button(b); if REPEAT[b] then held[b] = .35 end end
local function release(b) held[b] = nil end

function love.gamepadpressed(_, b) press(b) end
function love.gamepadreleased(_, b) release(b) end
-- PC keys: arrows, Q/W shoulders, Z=A, X=B, A=Y, S=X, Tab=SELECT, Esc=START
local KEYS = { left = "dpleft", right = "dpright", up = "dpup", down = "dpdown", q = "leftshoulder", w = "rightshoulder",
  z = "a", x = "b", s = "x", a = "y", tab = "back", escape = "start" }
function love.keypressed(k)
  if CONSOLE then return end
  if renaming then   -- PC: typing a name
    if k == "backspace" then renameBuf = renameBuf:gsub("[\1-\127\192-\255][\128-\191]*$", "")   -- the last letter, accents included
    elseif k == "return" or k == "kpenter" then finishRename(renameBuf)
    elseif k == "escape" then renaming = nil; love.keyboard.setTextInput(false) end
    return
  end
  if KEYS[k] then press(KEYS[k]) end
end
function love.textinput(s)
  if not renaming then return end
  if CONSOLE then finishRename(s) elseif #renameBuf < 40 then renameBuf = renameBuf .. s end
end
function love.keyreleased(k) if not CONSOLE and KEYS[k] then release(KEYS[k]) end end
function love.touchpressed(_, x, y) if CONSOLE then touchDown(x, y) end end
function love.touchmoved(_, x, y) if CONSOLE then touchMove(x, y) end end
function love.touchreleased() if CONSOLE then touchUp() end end
function love.mousepressed(x, y, btn, istouch)
  if CONSOLE or istouch then return end
  if btn == 1 then touchDown(x - BOTTOM_X, y - BOTTOM_Y)
  elseif btn == 2 then rotatePiece() end
end
function love.mousemoved(x, y, _, _, istouch) if not CONSOLE and not istouch then touchMove(x - BOTTOM_X, y - BOTTOM_Y) end end
function love.mousereleased(_, _, _, istouch) if not CONSOLE and not istouch then touchUp() end end

-- ---------------------------------------------------------------- LÖVE callbacks
--[[ Loading goes one step a frame, with the step's name on both screens: if the console crashes while
     loading, the screen shows which step it was (a crash dump alone doesn't say). ]]
local BOOT = {}
-- fonts first: the system font is one 3 MB block of memory, easier to find before the textures are in
BOOT[#BOOT + 1] = { "fonts", function() fonts.tiny, fonts.small, fonts.body, fonts.big = mkFont(9), mkFont(11), mkFont(14), mkFont(26) end }
for i = 1, A.pages do
  BOOT[#BOOT + 1] = { "texture " .. i .. "/" .. A.pages, function() pages[i] = love.graphics.newImage("gfx/atlas" .. i .. ".png") end }
end
BOOT[#BOOT + 1] = { "room", function() SALA.load() end }
BOOT[#BOOT + 1] = { "save", function()
  math.randomseed(os.time())
  load()
  P.setLang(S.lang or "en"); S.lang = P.lang()   -- English unless the player picked Portuguese (the EN|pt button)
  if not S.menu then starterMenu() end
  if not S.day then freshGame() end
  clampSel()
  syncWorld()
  buildCats()
  changed(); dirty = false
end }
BOOT[#BOOT + 1] = { "first frame", function() end }
local bootStep, bootShown = 1, false

function love.load()
  love.graphics.setDefaultFilter("nearest", "nearest")
  if love.graphics.set3D then pcall(love.graphics.set3D, false) end
end

local function drawBoot()
  love.graphics.clear(0.1, 0.05, 0.02)
  love.graphics.setColor(1, 1, 1)
  love.graphics.print("Pizza Magna", 10, 10)
  love.graphics.print("Loading: " .. BOOT[bootStep][1] .. " (" .. bootStep .. "/" .. #BOOT .. ")", 10, 30)
end

function love.update(dt)
  if BOOT[bootStep] then
    if bootShown then BOOT[bootStep][2](); bootStep = bootStep + 1; bootShown = false end
    return
  end
  for b, left in pairs(held) do
    left = left - dt
    if left <= 0 then button(b); left = .08 end
    held[b] = left
  end
  if toasts[1] then toasts[1].time = toasts[1].time - dt; if toasts[1].time <= 0 then table.remove(toasts, 1) end end
  if armed then armed.time = armed.time - dt; if armed.time <= 0 then armed = nil end end
  if anim then updateDay(dt) end
  if dirty then saveTimer = saveTimer + dt; if saveTimer > 1 then save(); saveTimer = 0 end end
end

function love.draw(screen)
  if BOOT[bootStep] then drawBoot(); bootShown = true; return end
  if screen == nil then   -- PC: top screen above, bottom screen centred below
    drawTopScreen()
    love.graphics.push(); love.graphics.translate(BOTTOM_X, BOTTOM_Y)
    love.graphics.setScissor(BOTTOM_X, BOTTOM_Y, 320, 240)
    col(hex("#000000")); love.graphics.rectangle("fill", 0, 0, 320, 240)
    drawBottom()
    love.graphics.setScissor(); love.graphics.pop()
    col(hex("#000000")); love.graphics.rectangle("fill", 0, 240, BOTTOM_X, 240); love.graphics.rectangle("fill", 360, 240, 40, 240)
  elseif screen == "bottom" then drawBottom()
  else drawTopScreen() end
end

function love.quit() if dirty then save() end end
