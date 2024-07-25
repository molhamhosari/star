from flask import Flask, request, jsonify
import openai
import logging
from langdetect import detect

app = Flask(__name__)

# إعداد مفتاح API الخاص بـ OpenAI مباشرة في الشيفرة
openai.api_key = "sk-proj-3vl35MNtFHo3XYS2aeRRT3BlbkFJaXO5czgDbrMKRa45MMit"

# إعداد التسجيل (logging)
logging.basicConfig(level=logging.DEBUG)

# قاموس للأسئلة والأجوبة من النص المقدم باللغات المختلفة
faq = {
    "ar": {
        "ما هو التحليل المالي؟": "التحليل المالي هو عملية تقييم الأنشطة المالية للشركة من خلال استخدام البيانات المالية.",
        "ما هي أدوات التحليل المالي؟": "أدوات التحليل المالي تشمل النسب المالية، التحليل الأفقي والرأسي، والتحليل بواسطة التدفقات النقدية.",
        "ما هي النسبة الحالية؟": "النسبة الحالية هي نسبة السيولة الحالية إلى الالتزامات الجارية، وتستخدم لتقييم قدرة الشركة على سداد ديونها القصيرة الأجل.",
        "ما هي النسبة السريعة؟": "النسبة السريعة هي نسبة السيولة السريعة (النقد والأوراق المالية القابلة للتداول والمدينون) إلى الالتزامات الجارية.",
        "ما هي نسبة السيولة النقدية؟": "نسبة السيولة النقدية هي نسبة النقد والأوراق المالية القابلة للتداول إلى الالتزامات الجارية.",
        "ما هي نسبة التداول؟": "نسبة التداول هي نسبة الأصول المتداولة إلى الخصوم المتداولة.",
        "ما هو التحليل الأفقي؟": "التحليل الأفقي يتضمن مقارنة البيانات المالية عبر فترات زمنية مختلفة لتحديد الاتجاهات والتغيرات.",
        "ما هو التحليل الرأسي؟": "التحليل الرأسي يتضمن تحليل بنود القوائم المالية من خلال نسبتها إلى بند رئيسي مثل المبيعات أو إجمالي الأصول.",
        "ما هي نسبة الربحية؟": "نسبة الربحية تقيس قدرة الشركة على تحقيق الربح مقارنة بإيراداتها أو أصولها أو حقوق المساهمين.",
        "ما هي نسبة الدين؟": "نسبة الدين تقيس مقدار الديون التي تتحملها الشركة مقارنة برأس المال الإجمالي.",
        "ما هي نسبة حقوق المساهمين؟": "نسبة حقوق المساهمين هي نسبة حقوق المساهمين إلى إجمالي الأصول.",
        "ما هو التدفق النقدي التشغيلي؟": "التدفق النقدي التشغيلي هو النقد المتولد من الأنشطة التشغيلية للشركة.",
        "ما هو التدفق النقدي الحر؟": "التدفق النقدي الحر هو النقد المتبقي بعد خصم النفقات الرأسمالية من التدفق النقدي التشغيلي.",
        "ما هي نسبة الفائدة المغطاة؟": "نسبة الفائدة المغطاة تقيس قدرة الشركة على تغطية مصاريف الفائدة من أرباحها التشغيلية."
    },
    "en": {
        "What is financial analysis?": "Financial analysis is the process of evaluating the financial activities of a company using financial data.",
        "What are the tools of financial analysis?": "Financial analysis tools include financial ratios, horizontal and vertical analysis, and cash flow analysis.",
        "What is the current ratio?": "The current ratio is the ratio of current assets to current liabilities, used to evaluate a company's ability to pay short-term debts.",
        "What is the quick ratio?": "The quick ratio is the ratio of quick assets (cash, marketable securities, and receivables) to current liabilities.",
        "What is the cash ratio?": "The cash ratio is the ratio of cash and marketable securities to current liabilities.",
        "What is the turnover ratio?": "The turnover ratio is the ratio of current assets to current liabilities.",
        "What is horizontal analysis?": "Horizontal analysis involves comparing financial data over different periods to identify trends and changes.",
        "What is vertical analysis?": "Vertical analysis involves analyzing financial statement items as a percentage of a base item such as sales or total assets.",
        "What is profitability ratio?": "Profitability ratios measure a company's ability to generate profit relative to its revenue, assets, or equity.",
        "What is debt ratio?": "Debt ratio measures the amount of debt a company has compared to its total capital.",
        "What is equity ratio?": "Equity ratio is the ratio of shareholders' equity to total assets.",
        "What is operating cash flow?": "Operating cash flow is the cash generated from a company's operating activities.",
        "What is free cash flow?": "Free cash flow is the cash remaining after deducting capital expenditures from operating cash flow.",
        "What is interest coverage ratio?": "Interest coverage ratio measures a company's ability to cover its interest expenses with its operating income."
    },
    "zh": {
        "什么是财务分析？": "财务分析是通过使用财务数据评估公司财务活动的过程。",
        "财务分析的工具是什么？": "财务分析工具包括财务比率、水平和垂直分析以及现金流分析。",
        "当前比率是什么？": "当前比率是指流动资产与流动负债的比率，用于评估公司偿还短期债务的能力。",
        "速动比率是什么？": "速动比率是速动资产（现金、可交易证券和应收账款）与流动负债的比率。",
        "现金比率是什么？": "现金比率是现金和可交易证券与流动负债的比率。",
        "周转率是什么？": "周转率是流动资产与流动负债的比率。",
        "什么是水平分析？": "水平分析涉及在不同期间比较财务数据以识别趋势和变化。",
        "什么是垂直分析？": "垂直分析涉及将财务报表项目作为基础项目（如销售或总资产）的百分比进行分析。",
        "盈利比率是什么？": "盈利比率衡量公司相对于其收入、资产或权益的盈利能力。",
        "债务比率是什么？": "债务比率衡量公司相对于其总资本的债务金额。",
        "权益比率是什么？": "权益比率是股东权益与总资产的比率。",
        "经营现金流是什么？": "经营现金流是公司从经营活动中产生的现金。",
        "自由现金流是什么？": "自由现金流是从经营现金流中扣除资本支出后剩余的现金。",
        "利息覆盖率是什么？": "利息覆盖率衡量公司用其经营收入支付利息费用的能力。"
    }
}

@app.route("/chat", methods=['POST'])
def chat():
    try:
        if request.content_type != 'application/json':
            return jsonify({"response": "Unsupported Media Type: Content-Type must be application/json"}), 415

        incoming_msg = request.json.get('message').strip()
        app.logger.debug(f"Received message: {incoming_msg}")

        # اكتشاف اللغة
        lang = detect(incoming_msg)
        app.logger.debug(f"Detected language: {lang}")

        # تعيين اللغة المناسبة أو الإنجليزية كافتراضية
        lang = lang if lang in faq else "en"

        # البحث عن الإجابة في القاموس
        if incoming_msg in faq[lang]:
            answer = faq[lang][incoming_msg]
        else:
            # إذا لم يكن السؤال في القاموس، اتصل بـ OpenAI API للحصول على رد ذكي
            answer = get_openai_response(incoming_msg, lang)
        
        app.logger.debug(f"Sending response: {answer}")
        return jsonify({"response": answer})
    except Exception as e:
        app.logger.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({"response": "عذرًا، حدث خطأ ما. يرجى المحاولة لاحقًا."}), 500

def get_openai_response(message, lang):
    try:
        # إعداد طلب OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Respond in {lang} to: {message}",
            max_tokens=150
        )
        # استخراج النص من الرد
        return response.choices[0].text.strip()
    except Exception as e:
        app.logger.error(f"Error in OpenAI API call: {str(e)}", exc_info=True)
        return "عذرًا، لا أستطيع معالجة طلبك حاليًا. يرجى المحاولة لاحقًا."

if __name__ == "__main__":
    app.run(debug=True)
