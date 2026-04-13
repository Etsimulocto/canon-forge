# ============================================================
# PATCH: add 4.99 pack for Canon Forge
# Run from ~/spiralside-api in Git Bash
# ============================================================

f = open('main.py', 'r', encoding='utf-8')
s = f.read()
f.close()

# Fix 1: add 4.99 to CREDIT_PACKS and add canon_forge flag
old = '''CREDIT_PACKS = {
    "5":  500,
    "10": 1100,
    "20": 2400,
}'''
new = '''CREDIT_PACKS = {
    "5":  500,
    "10": 1100,
    "20": 2400,
    "499": 0,  # Canon Forge lifetime unlock — no credits, sets is_paid only
}'''
assert s.count(old) == 1, 'anchor 1 not found'
s = s.replace(old, new, 1)

# Fix 2: add forge return URL to paypal order creation
old2 = '''                "application_context": {
                    "return_url": "https://www.spiralside.com/?payment=success",
                    "cancel_url": "https://www.spiralside.com/?payment=cancelled"
                }'''
new2 = '''                "application_context": {
                    "return_url": f"https://{'forge' if amount == '499' else 'www'}.spiralside.com/?payment=success",
                    "cancel_url": f"https://{'forge' if amount == '499' else 'www'}.spiralside.com/?payment=cancelled"
                }'''
assert s.count(old2) == 1, 'anchor 2 not found'
s = s.replace(old2, new2, 1)

# Fix 3: handle 499 pack in capture — sets is_paid, adds 0 credits
old3 = '''        credits_to_add = CREDIT_PACKS.get(amount, 500)
        # Add credits to user
        usage = sb.table("user_usage").select("*").eq("user_id", user_id).execute()
        if not usage.data:
            sb.table("user_usage").insert({"user_id": user_id, "credits": float(credits_to_add), "free_messages_today": 0, "last_reset_date": str(date.today()), "is_paid": True}).execute()
        else:
            current = usage.data[0]["credits"] or 0
            sb.table("user_usage").update({"credits": current + credits_to_add, "is_paid": True}).eq("user_id", user_id).execute()'''
new3 = '''        is_forge_unlock = (amount == "499")
        credits_to_add = CREDIT_PACKS.get(amount, 500)
        # Add credits to user
        usage = sb.table("user_usage").select("*").eq("user_id", user_id).execute()
        if not usage.data:
            sb.table("user_usage").insert({"user_id": user_id, "credits": float(credits_to_add), "free_messages_today": 0, "last_reset_date": str(date.today()), "is_paid": True}).execute()
        else:
            current = usage.data[0]["credits"] or 0
            update_data = {"is_paid": True}
            if not is_forge_unlock:
                update_data["credits"] = current + credits_to_add
            sb.table("user_usage").update(update_data).eq("user_id", user_id).execute()'''
assert s.count(old3) == 1, 'anchor 3 not found'
s = s.replace(old3, new3, 1)

# Fix 4: allow 499 in validation
old4 = '    if req.amount not in CREDIT_PACKS:\n        raise HTTPException(status_code=400, detail="Invalid amount. Choose 5, 10, or 20.")'
new4 = '    if req.amount not in CREDIT_PACKS:\n        raise HTTPException(status_code=400, detail="Invalid amount. Choose 5, 10, 20, or 499.")'
assert s.count(old4) == 1, 'anchor 4 not found'
s = s.replace(old4, new4, 1)

f = open('main.py', 'w', encoding='utf-8')
f.write(s)
f.close()
print('done')
