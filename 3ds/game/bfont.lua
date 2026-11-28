--[[ Text drawn from a bitmap font: gfx/font.png and fontdata.lua, made by tools/export_3ds_font.js (Nunito, at the
     exact pixel sizes tiny, small, body and big). Each letter is a piece of that picture drawn at whole pixels, so
     the text stays sharp on the console; its system font, scaled down, was blurred, and LÖVE Potion has no image
     fonts on the 3DS. Strings are UTF-8; a character missing from the font is drawn as "?". ]]
local FD = require("fontdata")
local M = {}
local img, quads
local CHARS = "[%z\1-\127\194-\244][\128-\191]*"
local function load()
  img = love.graphics.newImage("gfx/font.png"); img:setFilter("nearest", "nearest")
  local iw, ih = img:getDimensions()
  quads = {}
  for k, f in pairs(FD) do quads[k] = {}; for ch, g in pairs(f.g) do quads[k][ch] = love.graphics.newQuad(g[1], g[2], g[3], g[4], iw, ih) end end
end
function M.width(font, s)
  local g, w = FD[font].g, 0
  for ch in tostring(s):gmatch(CHARS) do w = w + (g[ch] or g["?"])[5] end
  return w
end
function M.line(font) return FD[font].line end   -- the height of one line of text
function M.print(font, s, x, y)
  if not img then load() end
  local f, q = FD[font], quads[font]
  local px, top = x, math.floor(y + .5) - math.floor((f.h - f.line) / 2)
  for ch in tostring(s):gmatch(CHARS) do
    local g = f.g[ch]
    if not g then ch = "?"; g = f.g[ch] end
    if ch ~= " " then love.graphics.draw(img, q[ch], math.floor(px + g[6] + .5), top) end
    px = px + g[5]
  end
end
-- the lines a text takes in a width (words kept whole; a line that fits stays as it is, spaces and all)
function M.wrap(font, s, w)
  local lines = {}
  for para in (tostring(s) .. "\n"):gmatch("(.-)\n") do
    if M.width(font, para) <= w then lines[#lines + 1] = para
    else
      local cur = ""
      for word in para:gmatch("%S+") do
        local try = cur == "" and word or cur .. " " .. word
        if cur ~= "" and M.width(font, try) > w then lines[#lines + 1] = cur; cur = word else cur = try end
      end
      lines[#lines + 1] = cur
    end
  end
  return lines
end
function M.printf(font, s, x, y, w, align)
  local lh = FD[font].line
  for i, l in ipairs(M.wrap(font, s, w)) do
    local lw = M.width(font, l)
    local lx = align == "center" and x + math.floor((w - lw) / 2) or align == "right" and x + w - lw or x
    M.print(font, l, lx, y + (i - 1) * lh)
  end
end
return M
