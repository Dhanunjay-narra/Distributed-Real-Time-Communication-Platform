import os, json

def test_frontend_project_structure():
    assert os.path.exists("apps/web/package.json")
    assert os.path.exists("apps/web/src/types/chat.ts")
    assert os.path.exists("apps/web/src/store/useChatStore.ts")
    assert os.path.exists("apps/web/src/components/ChatInterface.tsx")
    assert os.path.exists("apps/admin/package.json")
    assert os.path.exists("apps/admin/src/AdminDashboard.tsx")

    with open("apps/web/package.json", "r", encoding="utf-8") as f:
        web_pkg = json.load(f)
        assert web_pkg["name"] == "chatbot-web"
        assert "react" in web_pkg["dependencies"]
        assert "zustand" in web_pkg["dependencies"]
