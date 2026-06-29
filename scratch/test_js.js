const data = {
  detail: {
    message: "Ngày thi đăng ký phải bắt đầu từ ngày mai trở đi.",
    error_type: "ValidationError"
  }
};

async function readError(data, fallback) {
  if (typeof data.detail === "string") return data.detail;
  if (data.detail && typeof data.detail.message === "string") return data.detail.message;
  if (Array.isArray(data.detail)) return data.detail.map(item => item.msg).join("; ");
  return data.message || fallback;
}

readError(data, "fallback").then(console.log);
