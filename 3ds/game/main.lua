--[[ Pizza Magna for the Nintendo 3DS (LÖVE Potion), prototype: the Kitchen only.
     Bottom screen (touch): the bench, as in the browser game (320 wide, title strip on top, pizza, bowls, LCD).
     Top screen: the topping picker, dough and sauce, and the analysis (quality, cost, appeal, notes).
     On a PC (LÖVE 11/12) the window shows the top screen above the bottom one, and the mouse is the stylus. ]]
local P = require("pizza")
local D, A, t = P.D, P.A, P.t

local CONSOLE = love._console ~= nil or love.system.getOS() == "Horizon" or love.system.getOS() == "3DS"
local BOTTOM_X, BOTTOM_Y = 40, 240   -- where the bottom screen sits in the PC window

-- text only the 3DS port has (the browser game has no buttons to explain)
local L3 = {
  en = { keys1 = "</> topping   L/R group   Up dough   Down sauce",
         keys2 = "A cut   X turn   B undo   Y clear   SELECT EN/PT   START quit" },
  pt = { keys1 = "</> ingrediente   L/R grupo   Cima massa   Baixo molho",
         keys2 = "A picar   X rodar   B desfazer   Y limpar   SELECT EN/PT   START sair" },
}
local function l3(k) return L3[P.lang()][k] end

-- ---------------------------------------------------------------- state and save
local S = { dough = "napo", sauce = "tomate", pieces = {}, sel = "fiambre", cut = "w", rot = {}, found = {}, lang = nil }
local cleared = nil          -- the pizza the bin just cleared: undo on an empty bench brings it back
local dirty, saveTimer = false, 0
local toasts = {}
local an                     -- analysis of the pizza on the bench (recomputed on every change)

local function save()
  local rot = {}
  for k, v in pairs(S.rot) do rot[#rot + 1] = k .. ":" .. v end
  local lines = {
    "lang=" .. P.lang(), "dough=" .. S.dough, "sauce=" .. S.sauce, "sel=" .. S.sel, "cut=" .. S.cut,
    "rot=" .. table.concat(rot, ","), "found=" .. table.concat(S.found, ","), "pieces=" .. P.packPieces(S.pieces),
  }
  love.filesystem.write("save.txt", table.concat(lines, "\n") .. "\n")
  dirty = false
end
local function load()
  local ok, txt = pcall(love.filesystem.read, "save.txt")
  if not ok or not txt then return end
  local v = {}
  for k, val in txt:gmatch("(%w+)=([^\n]*)") do v[k] = val end
  if v.lang then S.lang = v.lang end
  if v.dough and D.DOUGHS[v.dough] then S.dough = v.dough end
  if v.sauce and D.SAUCES[v.sauce] then S.sauce = v.sauce end
  if v.sel and D.ING[v.sel] then S.sel = v.sel end
  if v.cut == "g" then S.cut = "g" end
  for k, n in (v.rot or ""):gmatch("([%w_]+):(%d)") do if D.ING[k] then S.rot[k] = tonumber(n) end end
  for id in (v.found or ""):gmatch("[%w_]+") do S.found[#S.found + 1] = id end
  if v.pieces and v.pieces ~= "" then pcall(function() S.pieces = P.unpackPieces(v.pieces) end) end
end

local function toast(s) toasts[#toasts + 1] = { s = s, time = 3 } end

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
  local piece = { i = S.sel, x = mid and 0 or x, y = mid and 0 or y, r = math.random() * 6.28, v = math.random(0, 2) }
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
local function setLang(l) P.setLang(l); S.lang = P.lang(); buildCats(); changed() end

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

local function drawBottom()
  love.graphics.setColor(1, 1, 1)
  spr("marble", BW / 2, 100); spr("marble", BW / 2, 140)
  -- the pizza and its shadow on the marble
  love.graphics.setColor(40 / 255, 30 / 255, 20 / 255, .32)
  love.graphics.ellipse("fill", PCX + 3, PCY + 4, PR + 1, PR)
  drawPizza(S, PCX, PCY)
  -- the name of the pizza on the strip on top
  benchLabel(P.upper(t("k.newname")), BW / 2, 6, C.ink, { 1, 1, 1, .4 })
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
  -- language button
  local L = LANG_BTN
  col(hex("#4a260f")); love.graphics.rectangle("fill", L.x, L.y, L.w, L.h)
  col(C.gold); love.graphics.rectangle("fill", L.x + 1, L.y + 1, L.w - 2, L.h - 2)
  benchLabel(P.lang() == "pt" and "PT|en" or "EN|pt", L.x + L.w / 2, L.y + 2, hex("#3a2706"), hex("#fbe39a", .8))
end

-- ---------------------------------------------------------------- top screen: picker and analysis
local function meter(x, y, w, h, v, c)
  col(hex("#000000", .45)); love.graphics.rectangle("fill", x, y, w, h)
  col(c); love.graphics.rectangle("fill", x, y, math.floor(w * v / 100 + .5), h)
end

local function drawTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  -- header
  col(C.panel); love.graphics.rectangle("fill", 0, 0, 400, 18)
  text("PIZZA MAGNA", 6, 3, "small", C.gold)
  text(t("k.book", { n = #S.found, t = #D.COMBOS }), 120, 3, "small", C.dim, "right", 274)
  -- left: the topping picker
  local cat = catOf(S.sel)
  local list = catList[cat]
  local k = idxIn(list, S.sel)
  text("L <", 6, 23, "small", C.dim)
  text(t("cat." .. cat) .. "  " .. k .. "/" .. #list, 6, 23, "small", C.cream, "center", 188)
  text("> R", 6, 23, "small", C.dim, "right", 188)
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
  -- toasts (combo found...)
  if toasts[1] then
    local s = toasts[1].s
    local w = math.min(380, fw("body", s) + 16)
    col(hex("#000000", .85)); love.graphics.rectangle("fill", 200 - w / 2, 213, w, 24)
    pxRect(200 - w / 2, 213, w, 24, C.gold)
    text(fitText(s, "body", w - 8), 200 - w / 2, 217, "body", C.combo, "center", w)
  end
end

-- ---------------------------------------------------------------- input
local drag = nil
local function benchPoint(x, y) return (x - PCX) / PR, (y - PCY) / PR end
local function touchDown(x, y)
  local L = LANG_BTN
  if x >= L.x and x <= L.x + L.w and y >= L.y and y <= L.y + L.h then setLang(P.lang() == "pt" and "en" or "pt"); return end
  for _, b in ipairs(BOWLS) do
    if x >= b.x - 6 and x <= b.x + BOWL_W + 6 and y - OY >= b.y - 4 and y - OY <= b.y + BOWL_H + 16 then setCut(b.g); return end
  end
  local px, py = benchPoint(x, y)
  if math.sqrt(px * px + py * py) > 1 then return end
  drag = { x = 9, y = 9 }
  if addPiece(px, py) then drag = { x = px, y = py } end
end
local function touchMove(x, y)
  if not drag then return end
  local px, py = benchPoint(x, y)
  if math.sqrt((px - drag.x) ^ 2 + (py - drag.y) ^ 2) > .2 and addPiece(px, py) then drag = { x = px, y = py } end
end
local function touchUp() drag = nil end

local held = {}
local function button(b)
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
  elseif b == "back" then setLang(P.lang() == "pt" and "en" or "pt")
  elseif b == "start" then save(); love.event.quit() end
end
local REPEAT = { dpleft = true, dpright = true }
local function press(b) button(b); if REPEAT[b] then held[b] = .35 end end
local function release(b) held[b] = nil end

function love.gamepadpressed(_, b) press(b) end
function love.gamepadreleased(_, b) release(b) end
-- PC keys: arrows, Q/W shoulders, Z=A, X=B, A=Y, S=X, Tab=SELECT, Esc=START
local KEYS = { left = "dpleft", right = "dpright", up = "dpup", down = "dpdown", q = "leftshoulder", w = "rightshoulder",
  z = "a", x = "b", s = "x", a = "y", tab = "back", escape = "start" }
function love.keypressed(k) if not CONSOLE and KEYS[k] then press(KEYS[k]) end end
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
BOOT[#BOOT + 1] = { "save", function()
  math.randomseed(os.time())
  load()
  P.setLang(S.lang or "en"); S.lang = P.lang()   -- English unless the player picked Portuguese (SELECT or the EN|pt button)
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
  if dirty then saveTimer = saveTimer + dt; if saveTimer > 1 then save(); saveTimer = 0 end end
end

function love.draw(screen)
  if BOOT[bootStep] then drawBoot(); bootShown = true; return end
  if screen == nil then   -- PC: top screen above, bottom screen centred below
    drawTop()
    love.graphics.push(); love.graphics.translate(BOTTOM_X, BOTTOM_Y)
    love.graphics.setScissor(BOTTOM_X, BOTTOM_Y, 320, 240)
    col(hex("#000000")); love.graphics.rectangle("fill", 0, 0, 320, 240)
    drawBottom()
    love.graphics.setScissor(); love.graphics.pop()
    col(hex("#000000")); love.graphics.rectangle("fill", 0, 240, BOTTOM_X, 240); love.graphics.rectangle("fill", 360, 240, 40, 240)
  elseif screen == "bottom" then drawBottom()
  else drawTop() end
end

function love.quit() if dirty then save() end end
