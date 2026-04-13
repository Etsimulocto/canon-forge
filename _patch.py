f = open('public/index.html', 'r', encoding='utf-8')
s = f.read()
f.close()

# Fix 1: hide uses bar for paid users, show for free
old3 = "  const barFill = document.getElementById('uses-bar-fill');\n  const barCount = document.getElementById('uses-bar-count');\n\n  if (isPaid) {\n    badge.textContent = 'unlimited';\n    badge.className = 'uses-badge good';\n    barFill.style.width = '100%';\n    barCount.textContent = 'unlimited';\n    return;\n  }"
new3 = "  const barFill = document.getElementById('uses-bar-fill');\n  const barCount = document.getElementById('uses-bar-count');\n  const barWrap = document.getElementById('uses-bar-wrap');\n\n  if (isPaid) {\n    badge.textContent = 'unlimited';\n    badge.className = 'uses-badge good';\n    barWrap.style.display = 'none';\n    return;\n  }\n  barWrap.style.display = 'block';"
assert s.count(old3) == 1, 'anchor not found: ' + repr(old3[:40])
s = s.replace(old3, new3, 1)

f = open('public/index.html', 'w', encoding='utf-8')
f.write(s)
f.close()
print('done')
