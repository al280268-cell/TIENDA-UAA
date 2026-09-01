with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find where the error is shown in liveLaunch and make it very visible
old_err = """        showToast("Error: " + detail, "error");
        const statusEl2 = document.getElementById("live-status-msg");
        if (statusEl2) statusEl2.innerHTML = `<span style="color:#E62429">\u274c ${detail}</span>`;"""

# replace all instances where the error is shown after !ok with a more visible one
import re
idx = text.find("async function liveLaunch()")
end = text.find("\n    async function liveConnect()", idx)
launch_fn = text[idx:end]

# Show what we have around the error handling
err_idx = launch_fn.find("showToast(\"Error:")
safe = re.sub(r"[^\x00-\x7F]", "?", launch_fn[max(0,err_idx-100):err_idx+400])
print("Error handling area:")
print(safe)
