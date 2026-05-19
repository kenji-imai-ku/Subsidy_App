from app.core.database import SessionLocal, engine, Base
from app.models.support_program import SupportProgram, SupportProgramCondition
from app.models.program_source import ProgramSource
from app.core.constants import SupportType, Category, ConfidenceLevel, ApplicationMethod, BenefitAmountType, BenefitUnit
import app.models
from sqlalchemy.orm import Session


def seed_programs_data(db: Session):
    # 重複防止ロジック
    def get_or_create_program(title, provider, **kwargs):
        existing = db.query(SupportProgram).filter_by(title=title, provider=provider).first()
        if existing:
            return existing
        program = SupportProgram(title=title, provider=provider, **kwargs)
        db.add(program)
        return program

    programs_data = [
        {
            "title": "住居確保給付金",
            "provider": "京都市",
            "summary": "離職等により住居を失うおそれがある方に家賃相当額を支給します。",
            "benefit": "家賃相当額（上限あり）を支給",
            "category": "housing",
            "support_type": "subsidy",
            "benefit_amount_type": "max_amount",
            "benefit_unit": "per_household",
            "target_prefecture": "京都府",
            "target_city": "京都市",
            "application_required": True,
            "application_method": "counter",
            "confidence_level": "official",
            "condition": {
                "requires_unemployed": True,
                "requires_income_decreased": True,
                "max_annual_income": 2000000,
                "requires_rent": True,
                "condition_description": "離職・廃業から2年以内、または給与等が個人の責任によらず減少した方が対象です。"
            }
        },
        {
            "title": "子ども医療費支給制度",
            "provider": "京都市",
            "summary": "子どもの医療費の自己負担額を一部助成します。",
            "benefit": "医療費の自己負担分を助成（一部自己負担あり）",
            "category": "childcare",
            "support_type": "medical",
            "benefit_amount_type": "depends",
            "target_prefecture": "京都府",
            "target_city": "京都市",
            "application_required": True,
            "application_method": "counter",
            "confidence_level": "official",
            "condition": {
                "max_age": 15,
                "requires_children": True,
                "requires_health_insurance": True,
                "condition_description": "京都市に居住し、健康保険に加入している中学校卒業までの子どもが対象です。"
            }
        },
        {
            "title": "ひとり親家庭等医療費支給制度",
            "provider": "京都市",
            "summary": "ひとり親家庭の方などの医療費の自己負担額を助成します。",
            "benefit": "医療費の自己負担分を助成",
            "category": "childcare",
            "support_type": "medical",
            "target_prefecture": "京都府",
            "target_city": "京都市",
            "application_required": True,
            "application_method": "counter",
            "confidence_level": "official",
            "condition": {
                "requires_single_parent": True,
                "max_annual_income": 3000000,
                "condition_description": "ひとり親家庭の父母、児童などが対象です。所得制限があります。"
            }
        },
        {
            "title": "育児支援ヘルパー派遣事業",
            "provider": "京都市",
            "summary": "産後の家事や育児を支援するため、ヘルパーを派遣します。",
            "benefit": "ヘルパーによる家事・育児支援（有料）",
            "category": "childcare",
            "support_type": "service_dispatch",
            "target_prefecture": "京都府",
            "target_city": "京都市",
            "application_required": True,
            "application_method": "counter",
            "confidence_level": "official",
            "condition": {
                "requires_pregnancy": False,
                "max_postpartum_months": 12,
                "condition_description": "産後1年以内で、家事や育児が困難な世帯が対象です。"
            }
        },
        {
            "title": "日常生活用具の給付",
            "provider": "自治体",
            "summary": "障害のある方の日常生活を容易にするため、用具を給付または貸与します。",
            "benefit": "特殊寝台、入浴補助用具などの給付・貸与",
            "category": "disability",
            "support_type": "goods",
            "application_required": True,
            "application_method": "counter",
            "confidence_level": "manual_checked",
            "condition": {
                "requires_disability": True,
                "manual_check_required": True,
                "condition_description": "身体障害者手帳等をお持ちの方で、種目ごとに定められた要件を満たす必要があります。"
            }
        },
        {
            "title": "生活福祉資金貸付制度",
            "provider": "社会福祉協議会",
            "summary": "低所得世帯、障害者世帯等に対し、資金の貸付けと必要な相談支援を行います。",
            "benefit": "生活費、入学資金などの貸付け",
            "category": "livelihood",
            "support_type": "loan",
            "application_required": True,
            "application_method": "counter",
            "confidence_level": "official",
            "condition": {
                "manual_check_required": True,
                "condition_description": "低所得世帯、障害者世帯、高齢者世帯が対象です。審査があります。"
            }
        },
        {
            "title": "電力・ガス・食料品等価格高騰緊急支援給付金",
            "provider": "国",
            "summary": "物価高騰の影響を大きく受ける低所得世帯を支援します。",
            "benefit": "1世帯あたり7万円または3万円など（時期により異なる）",
            "category": "livelihood",
            "support_type": "cash",
            "benefit_amount_type": "fixed",
            "benefit_unit": "per_household",
            "application_required": False,
            "application_method": "automatic",
            "confidence_level": "official",
            "condition": {
                "requires_tax_exempt": True,
                "condition_description": "住民税非課税世帯などが対象です。対象世帯にはプッシュ型で通知されます。"
            }
        },
        {
            "title": "就学援助制度",
            "provider": "京都市教育委員会",
            "summary": "経済的な理由で就学が困難な世帯に対し、学用品費などを援助します。",
            "benefit": "学用品費、給食費、修学旅行費などの援助",
            "category": "education",
            "support_type": "subsidy",
            "target_prefecture": "京都府",
            "target_city": "京都市",
            "application_required": True,
            "application_method": "counter",
            "confidence_level": "official",
            "condition": {
                "max_age": 15,
                "requires_children": True,
                "requires_household_head": False,
                "condition_description": "小・中学校に在籍する児童生徒の保護者で、所得が一定基準以下の方が対象です。"
            }
        },
        {
            "title": "産後ケア事業（宿泊型・通所型）",
            "provider": "京都市",
            "summary": "母子の健康維持と育児不安の解消のため、助産師等のケアを提供します。",
            "benefit": "助産所等での宿泊・日帰り・訪問ケア",
            "category": "childcare",
            "support_type": "service_discount",
            "target_prefecture": "京都府",
            "target_city": "京都市",
            "application_required": True,
            "application_method": "counter",
            "confidence_level": "official",
            "condition": {
                "max_postpartum_months": 4,
                "requires_pregnancy": False,
                "condition_description": "産後4か月未満（施設により異なる）の母子で、育児支援を必要とする方が対象です。"
            }
        },
        {
            "title": "高額療養費制度",
            "provider": "厚生労働省",
            "summary": "医療機関等で支払う窓口負担が、1か月で上限額を超えた場合に、超えた分を支給します。",
            "benefit": "自己負担限度額を超えた額の払い戻し",
            "category": "medical",
            "support_type": "subsidy",
            "application_required": True,
            "application_method": "mail",
            "confidence_level": "official",
            "condition": {
                "requires_health_insurance": True,
                "manual_check_required": True,
                "condition_description": "公的医療保険に加入している方が対象です。所得に応じて限度額が異なります。"
            }
        }
    ]

    count = 0
    for data in programs_data:
        condition_data = data.pop("condition", None)
        title = data.pop("title")
        provider = data.pop("provider")
        program = get_or_create_program(title, provider, **data)
        
        if condition_data:
            if not program.condition:
                program.condition = SupportProgramCondition(**condition_data)
            else:
                for key, value in condition_data.items():
                    setattr(program.condition, key, value)
        
        # Add a dummy source for each
        if not program.sources:
            program.sources.append(ProgramSource(
                source_url=f"https://example.com/programs/{program.id}",
                source_type="html",
                title=program.title,
                publisher=program.provider
            ))
        
        count += 1

    db.commit()
    return {"inserted": count, "message": "Seed programs processed successfully"}


def seed_programs():
    # CLI実行用
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        result = seed_programs_data(db)
        print(result["message"])
    finally:
        db.close()


if __name__ == "__main__":
    seed_programs()
