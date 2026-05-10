from app.core.database import SessionLocal
from app.models.support_program import SupportProgram, SupportProgramCondition


def seed_programs():
    db = SessionLocal()

    try:
        existing = db.query(SupportProgram).first()
        if existing:
            print("Seed data already exists")
            return

        programs = [
            SupportProgram(
                title="住居確保給付金",
                provider="京都市",
                summary="離職等により住居を失うおそれがある方に家賃相当額を支給する制度です。",
                benefit="家賃相当額を一定期間支給",
                category="housing",
                target_prefecture="京都府",
                target_city="京都市",
                target_ward=None,
                application_url="https://example.com/housing",
                source_url="https://example.com/source/housing",
                is_active=True,
                condition=SupportProgramCondition(
                    max_annual_income=4_000_000,
                    condition_description="収入が一定額以下であること等",
                ),
            ),
            SupportProgram(
                title="子育て世帯生活支援特別給付金",
                provider="国・自治体",
                summary="子育て世帯の生活を支援するための給付金です。",
                benefit="対象児童1人あたり一定額を支給",
                category="childcare",
                target_prefecture=None,
                application_url="https://example.com/childcare",
                source_url="https://example.com/source/childcare",
                is_active=True,
                condition=SupportProgramCondition(
                    requires_children=True,
                    min_children_count=1,
                    condition_description="子どもがいる世帯が対象です。",
                ),
            ),
            SupportProgram(
                title="低所得世帯向け給付金",
                provider="自治体",
                summary="住民税非課税世帯等を対象とした給付金です。",
                benefit="一定額を支給",
                category="low_income",
                target_prefecture=None,
                application_url="https://example.com/low-income",
                source_url="https://example.com/source/low-income",
                is_active=True,
                condition=SupportProgramCondition(
                    requires_tax_exempt=True,
                    condition_description="住民税非課税世帯等が対象です。",
                ),
            ),
        ]

        db.add_all(programs)
        db.commit()
        print("Seed data inserted")

    finally:
        db.close()


if __name__ == "__main__":
    seed_programs()
