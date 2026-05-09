<template>
  <div class="chatbot-root">
    <button v-if="!isOpen" class="chat-fab" @click="openPanel" aria-label="打开智能助手">
      <span class="chat-fab-ring"></span>
      <span class="chat-fab-core">
        <svg class="chat-fab-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M12 2a1 1 0 0 1 1 1v1.08a8 8 0 0 1 6.92 6.92H21a1 1 0 1 1 0 2h-1.08a8 8 0 0 1-6.92 6.92V21a1 1 0 1 1-2 0v-1.08a8 8 0 0 1-6.92-6.92H3a1 1 0 1 1 0-2h1.08A8 8 0 0 1 11 4.08V3a1 1 0 0 1 1-1Zm0 4a6 6 0 1 0 0 12 6 6 0 0 0 0-12Zm-2.2 5.7a1 1 0 1 1 0-2h4.4a1 1 0 1 1 0 2Zm0 3.6a1 1 0 1 1 0-2h4.4a1 1 0 1 1 0 2Z"
          />
        </svg>
      </span>
      <span class="chat-fab-tag">智能问答</span>
    </button>

    <div v-else class="chat-panel">
      <div class="chat-header">
        <div class="chat-title">流量智能助手</div>
        <button class="chat-close" @click="closePanel" aria-label="关闭聊天窗口">×</button>
      </div>

      <div class="chat-messages" ref="messageBox">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="chat-msg"
          :class="msg.role === 'user' ? 'chat-msg-user' : 'chat-msg-assistant'"
        >
          {{ msg.content }}
        </div>
        <div v-if="loading" class="chat-msg chat-msg-assistant">正在分析当前看板数据...</div>
      </div>

      <div class="chat-input-wrap">
        <input
          v-model.trim="inputText"
          class="chat-input"
          type="text"
          placeholder="例如：当前流量最高IP是谁？"
          @keyup.enter="sendMessage"
        />
        <button class="chat-send" :disabled="loading || !inputText" @click="sendMessage">发送</button>
      </div>
    </div>
  </div>
</template>

<script>
import http from "@/api/http";

export default {
  name: "ChatBotWidget",
  data() {
    return {
      isOpen: false,
      loading: false,
      inputText: "",
      messages: [
        {
          role: "assistant",
          content:
            "你好，我可以基于当前流量看板回答：概览、流量最高IP、最近告警、协议分布。",
        },
      ],
    };
  },
  methods: {
    openPanel() {
      this.isOpen = true;
      this.$nextTick(this.scrollToBottom);
    },
    closePanel() {
      this.isOpen = false;
    },
    scrollToBottom() {
      const box = this.$refs.messageBox;
      if (!box) return;
      box.scrollTop = box.scrollHeight;
    },
    async sendMessage() {
      if (!this.inputText || this.loading) return;
      const question = this.inputText;
      this.inputText = "";
      this.messages.push({ role: "user", content: question });
      this.loading = true;
      this.$nextTick(this.scrollToBottom);

      try {
        const history = this.messages.slice(-12);
        const res = await http.post(
          "/api/chat/ask",
          { question, history },
          { timeout: 30000 }
        );
        const answer = res?.data?.answer || "暂时无法回答这个问题，请稍后重试。";
        this.messages.push({ role: "assistant", content: answer });
      } catch (err) {
        const status = err?.response?.status;
        const backendMsg = err?.response?.data?.answer || err?.response?.data?.detail;
        if (err?.code === "ECONNABORTED") {
          this.messages.push({
            role: "assistant",
            content: "模型响应超时（30秒），请稍后重试或简化问题。",
          });
        } else if (status) {
          this.messages.push({
            role: "assistant",
            content: backendMsg
              ? `请求失败（${status}）：${backendMsg}`
              : `请求失败（${status}），请检查后端日志。`,
          });
        } else {
          this.messages.push({
            role: "assistant",
            content: "聊天服务连接失败，请确认后端 API 已启动。",
          });
        }
        console.error("chat ask failed:", err);
      } finally {
        this.loading = false;
        this.$nextTick(this.scrollToBottom);
      }
    },
  },
};
</script>

<style scoped>
.chatbot-root {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 9999;
}

.chat-fab {
  width: 70px;
  height: 70px;
  border: none;
  border-radius: 50%;
  background: transparent;
  cursor: pointer;
  position: relative;
  display: grid;
  place-items: center;
  transition: transform 0.25s ease, filter 0.25s ease;
  animation: fabFloat 2.6s ease-in-out infinite;
}

.chat-fab:hover {
  transform: translateY(-3px) scale(1.03);
  filter: brightness(1.08);
}

.chat-fab-ring {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    rgba(0, 245, 255, 0.95),
    rgba(0, 117, 255, 0.9),
    rgba(0, 58, 255, 0.82),
    rgba(0, 245, 255, 0.95)
  );
  filter: blur(1px);
  animation: fabSpin 5s linear infinite, fabPulse 2.2s ease-in-out infinite;
}

.chat-fab-core {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at 30% 25%, rgba(255, 255, 255, 0.36), rgba(255, 255, 255, 0) 36%),
    linear-gradient(140deg, #0259ff 0%, #00b6ff 58%, #00e6ff 100%);
  box-shadow:
    inset 0 1px 8px rgba(255, 255, 255, 0.42),
    0 10px 28px rgba(0, 132, 255, 0.58);
}

.chat-fab-icon {
  width: 32px;
  height: 32px;
  fill: #eaffff;
  filter: drop-shadow(0 1px 5px rgba(0, 0, 0, 0.28));
}

.chat-fab-tag {
  position: absolute;
  right: 78px;
  top: 50%;
  transform: translateY(-50%);
  color: #dff6ff;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
  white-space: nowrap;
  padding: 5px 10px;
  border: 1px solid rgba(0, 216, 255, 0.48);
  border-radius: 999px;
  background: rgba(8, 40, 86, 0.88);
  backdrop-filter: blur(6px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.chat-fab:hover .chat-fab-tag {
  opacity: 1;
  transform: translateY(-50%) translateX(-2px);
}

@keyframes fabSpin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes fabPulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(0, 224, 255, 0.55);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(0, 224, 255, 0);
  }
}

@keyframes fabFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

.chat-panel {
  width: 350px;
  height: 470px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(9, 23, 49, 0.96);
  border: 1px solid rgba(0, 166, 255, 0.55);
  box-shadow: 0 10px 35px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
}

.chat-header {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  background: linear-gradient(90deg, rgba(0, 98, 255, 0.35), rgba(0, 198, 255, 0.2));
  color: #dff6ff;
}

.chat-title {
  font-size: 14px;
  font-weight: 700;
}

.chat-close {
  border: none;
  background: transparent;
  color: #dff6ff;
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chat-msg {
  max-width: 85%;
  padding: 8px 10px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.45;
  white-space: pre-wrap;
}

.chat-msg-user {
  align-self: flex-end;
  background: #0a67ff;
  color: #fff;
}

.chat-msg-assistant {
  align-self: flex-start;
  background: rgba(0, 156, 255, 0.2);
  color: #dff6ff;
}

.chat-input-wrap {
  padding: 10px;
  border-top: 1px solid rgba(0, 156, 255, 0.35);
  display: flex;
  gap: 8px;
}

.chat-input {
  flex: 1;
  height: 34px;
  border-radius: 6px;
  border: 1px solid rgba(0, 156, 255, 0.45);
  padding: 0 10px;
  outline: none;
  background: rgba(9, 23, 49, 0.75);
  color: #eef9ff;
}

.chat-send {
  min-width: 54px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #fff;
  background: linear-gradient(135deg, #0062ff, #00a6ff);
}

.chat-send:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 768px) {
  .chatbot-root {
    right: 12px;
    bottom: 12px;
  }

  .chat-fab {
    width: 62px;
    height: 62px;
  }

  .chat-fab-icon {
    width: 28px;
    height: 28px;
  }

  .chat-fab-tag {
    display: none;
  }

  .chat-panel {
    width: calc(100vw - 24px);
    height: 62vh;
  }
}
</style>
