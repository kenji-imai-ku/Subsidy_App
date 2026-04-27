"use client";
import { useEffect, useState } from "react";

export default function PlaygroundPage() {
  const [msg, setMsg] = useState("接続中...");

  useEffect(() => {
    // FastAPIのルートパス (/) を取得
    fetch("http://localhost:8000/")
      .then((res) => res.json())
      .then((data) => setMsg(data.message))
      .catch((err) => {
        console.error("Error:", err);
        setMsg("バックエンドが起動していないようです 😭");
      });
  }, []);

  return (
    <div style={{ 
      display: "flex", 
      flexDirection: "column", 
      alignItems: "center", 
      marginTop: "100px",
      fontFamily: "sans-serif"
    }}>
      <h1>🚀 Playground: 疎通確認</h1>
      <div style={{
        padding: "20px",
        borderRadius: "10px",
        background: "#f0f0f0",
        border: "1px solid #ccc",
        fontSize: "1.2rem",
        color: "#333"
      }}>
        {msg}
      </div>
    </div>
  );
}
