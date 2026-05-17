from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.routers import profiles, programs, matches, program_statuses
import app.models  # テーブル定義を読み込ませるためにインポート

# アプリ起動時にテーブルを作成する
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Support Matching API")

# フロントエンド（Next.js）からのアクセスを許可する設定（CORS）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(profiles.router)
app.include_router(programs.router)
app.include_router(matches.router)
app.include_router(program_statuses.router)


@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
