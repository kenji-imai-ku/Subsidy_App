export type NotificationCategory = "newBenefit" | "deadline" | "season";

export type NotificationItem = {
  id: string;
  category: NotificationCategory;
  label: string;
  title: string;
  date: string;
  emailSubject: string;
  emailLead: string;
  detailMessage: string;
  benefitDetail?: {
    name: string;
    provider: string;
    flag: string;
    statusLabel: string;
    score: number;
    amount: string;
    deadline: string;
    supportType: string;
    applicationMethod: string;
    confidenceLabel: string;
    target: string;
    overview: string;
    reasons: readonly string[];
    warnings: readonly string[];
  };
  emailBody: readonly string[];
  nextActions: readonly string[];
};

export const notifications = [
  {
    id: "new-childcare-benefit",
    category: "newBenefit",
    label: "新着の給付金",
    title: "子育て世帯生活支援特別給付金が対象候補に追加されました",
    date: "2026/05/19 10:30",
    emailSubject: "【給付金サポート】子育て世帯生活支援特別給付金が対象候補に追加されました",
    emailLead: "入力いただいた条件に照らすと、子育て世帯生活支援特別給付金に該当する可能性があります。",
    detailMessage: "受け取れる可能性のある新着の給付金が追加されました。",
    benefitDetail: {
      name: "子育て世帯生活支援特別給付金",
      provider: "京都市",
      flag: "おすすめ",
      statusLabel: "条件に合致",
      score: 94,
      amount: "1世帯あたり 50,000円",
      deadline: "2026/06/30（火）",
      supportType: "現金給付",
      applicationMethod: "オンライン / 窓口",
      confidenceLabel: "確認済み",
      target: "子育て世帯 / 所得条件あり",
      overview: "子どもがいる世帯を対象に、生活費の一部を支援する給付金です。",
      reasons: [
        "子どもがいる世帯向け条件に合致しています",
        "居住地が対象地域に合致しています",
      ],
      warnings: [],
    },
    emailBody: [
      "子どもがいる世帯を対象に、生活費の一部を支援する給付金です。",
      "世帯構成や所得条件によって受給可否が変わります。",
    ],
    nextActions: [
      "給付金一覧画面でマッチ度と確認事項を確認する",
      "子どもの人数と所得条件を確認する",
    ],
  },
  {
    id: "new-livelihood-support",
    category: "newBenefit",
    label: "新着の給付金",
    title: "生活支援給付金が対象候補に追加されました",
    date: "2026/05/18 09:00",
    emailSubject: "【給付金サポート】生活支援給付金が対象候補に追加されました",
    emailLead: "世帯年収や居住地域の条件から、生活支援系の給付金に該当する可能性があります。",
    detailMessage: "受け取れる可能性のある新着の給付金が追加されました。",
    benefitDetail: {
      name: "生活支援給付金",
      provider: "京都府",
      flag: "確認が必要",
      statusLabel: "確認後に対象の可能性",
      score: 82,
      amount: "最大 30,000円",
      deadline: "2026/07/15（水）",
      supportType: "現金給付",
      applicationMethod: "窓口",
      confidenceLabel: "推定を含む",
      target: "低所得世帯 / 京都府内",
      overview: "生活費の負担軽減を目的とした給付金です。",
      reasons: [
        "居住地が対象地域に合致しています",
        "所得条件に合致している可能性があります",
      ],
      warnings: [
        "所得条件の境界線付近です。正確な所得による確認が必要です",
      ],
    },
    emailBody: [
      "生活費の負担軽減を目的とした給付金情報が追加されました。",
      "世帯年収や住民税の課税状況などで対象可否が変わります。",
    ],
    nextActions: [
      "給付金一覧画面で新着制度を確認する",
      "世帯年収と非課税世帯の入力内容を確認する",
    ],
  },
  {
    id: "housing-deadline",
    category: "deadline",
    label: "締め切りが近い",
    title: "住居確保給付金の申請期限が近づいています",
    date: "2026/05/17 08:45",
    emailSubject: "【給付金サポート】住居確保給付金の申請期限が近づいています",
    emailLead: "住居確保給付金の申請期限が近づいています。申請予定の場合は早めの確認をおすすめします。",
    detailMessage: "住居確保給付金の申請期限が近づいています。申請の予定がある場合はお早めにご確認ください。",
    benefitDetail: {
      name: "住居確保給付金",
      provider: "京都市",
      flag: "期限が近い",
      statusLabel: "確認後に対象の可能性",
      score: 86,
      amount: "家賃相当額（上限あり）",
      deadline: "2026/05/31（日）",
      supportType: "助成",
      applicationMethod: "窓口",
      confidenceLabel: "公式情報",
      target: "離職中 / 収入減少 / 賃貸住宅",
      overview: "住居を失うおそれがある方に、家賃相当額を支援する制度です。",
      reasons: [
        "居住地が対象地域に合致しています",
        "賃貸住宅にお住まいの条件を満たしています",
      ],
      warnings: [
        "収入減少の有無について確認が必要です",
      ],
    },
    emailBody: [
      "離職や収入減少などにより、住居を失うおそれがある方を支援する制度です。",
      "申請期限は2026年5月31日（日）までの想定です。",
    ],
    nextActions: [
      "申請期限と受付窓口を確認する",
      "賃貸契約書と収入状況がわかる書類を準備する",
    ],
  },
  {
    id: "scholarship-season",
    category: "season",
    label: "その他",
    title: "もうすぐ奨学金・就学支援の申請シーズンです",
    date: "2026/05/15 17:00",
    emailSubject: "【給付金サポート】奨学金・就学支援の申請シーズンが近づいています",
    emailLead: "6月から夏にかけて、奨学金や就学支援制度の案内が増える時期です。",
    detailMessage: "6月から夏にかけて、奨学金や就学支援制度の案内が増える時期です。こちらでも確認でき次第お知らせしますが、受け取る予定のある方はご自身でも早めにご確認ください。",
    emailBody: [
      "給付型奨学金、就学援助、授業料減免などの案内が増える時期です。",
      "世帯収入や在学状況の確認が必要になる場合があります。",
    ],
    nextActions: [
      "学校または自治体からの案内時期を確認する",
      "世帯収入を証明できる書類を準備する",
    ],
  },
  {
    id: "medical-season",
    category: "season",
    label: "その他",
    title: "夏前に医療費助成の更新案内が始まります",
    date: "2026/05/14 12:00",
    emailSubject: "【給付金サポート】医療費助成の更新案内が始まる時期です",
    emailLead: "自治体によっては、夏前から医療費助成や福祉医療証の更新案内が始まります。",
    detailMessage: "夏前にかけて、医療費助成や福祉医療証の更新案内が始まる時期です。こちらでも確認でき次第お知らせしますが、対象になりそうな方はご自身でも早めにご確認ください。",
    emailBody: [
      "医療費助成や福祉医療証の更新案内が始まる時期です。",
      "健康保険や所得状況によって更新条件が変わる場合があります。",
    ],
    nextActions: [
      "自治体からの更新案内を確認する",
      "健康保険証と本人確認書類を準備する",
    ],
  },
] as const satisfies readonly NotificationItem[];

export const categoryTone = {
  newBenefit: {
    badge: "bg-emerald-100 text-emerald-700",
  },
  deadline: {
    badge: "bg-amber-100 text-amber-700",
  },
  season: {
    badge: "bg-sky-100 text-sky-700",
  },
} as const satisfies Record<NotificationCategory, { badge: string }>;
