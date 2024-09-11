from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Optional, Literal
from pathlib import Path
from loguru import logger
import json
import os

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://api.deepbricks.ai/v1/"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

class Author(BaseModel):
    name: str
    affiliation: Optional[str]
    email: Optional[str]
    
class BasicInfo(BaseModel):
    title: str
    keywords: list[str]
    authors: list[Author]
    doi: Optional[str]

class Hazard(BaseModel):
    earthquake: Optional[bool]
    strong_wind: Optional[bool]
    scour: Optional[bool]
    soil_liquefication: Optional[bool]
    tsunami: Optional[bool]
    landslide: Optional[bool] = Field(description="or debris flow")
    corrosion: Optional[bool]
    storm_surge: Optional[bool] = Field(description="or wave surge")
    flooding: Optional[bool]
    ground_moving: Optional[bool]
    fire: Optional[bool]
    explosion: Optional[bool]
    climate_change: Optional[bool]

class BridgeType(BaseModel):
    beam_bridge: bool
    arch_bridge: bool
    cable_stayed_bridge: bool
    suspension_bridge: bool

class ResearchSubject(BaseModel):
    hazard: Hazard
    bridge: BridgeType

class TimeScale(BaseModel): 
    # 短期多灾害组合：多种灾害在短时间内同时发生，持续时间接近单一灾害。
    single_disaster_combination: bool = Field(description="Multiple disasters occur simultaneously in a short time, similar to the duration of a single disaster.")

    # 长期多灾害链：多种灾害在较长时间内多次或持续发生，显著超过单一灾害持续时间。
    multiple_disaster_chain: bool = Field(description="Multiple disasters occur repeatedly or continuously over a longer period, exceeding the duration of a single disaster.")

    # 生命周期威胁：灾害在结构的整个生命周期中持续存在，如冲刷、腐蚀等。
    life_cycle: bool = Field(description="Disasters pose a continuous threat throughout the structure's lifecycle, such as scour or corrosion.")

class SpatialScale(BaseModel): 
    # 组件级：关注桥梁的单个部件，如桥墩和支座。
    component: bool = Field(description="Focus on individual bridge components, such as piers and bearings.")

    # 整体结构（不考虑场地）：只考虑整个桥梁，不涉及场地条件或场地-结构相互作用。
    structure_without_site: bool = Field(description="Consider the entire bridge without site conditions or site-structure interaction.")

    # 整体结构（考虑场地）：同时考虑桥梁和场地条件，包含场地-结构相互作用。
    structure_with_site: bool = Field(description="Consider both the bridge and site conditions, including site-structure interaction.")

    # 区域或网络：关注一个地区内的多座桥梁或桥梁网络。
    region_or_network: bool = Field(description="Consider multiple bridges within a region or a bridge network.")

class SpecialSite(BaseModel): 
    # 靠近断层：桥梁位于地震断层附近。
    near_fault: bool
    # 受冲刷影响：桥梁处于冲刷影响区。
    under_scour: bool
    # 易液化：场地易液化。
    liquefiable: bool = Field(description="easy to liquefy.")
    # 其他：其他特殊场地条件。
    other: Optional[str] = Field(description="Other special site conditions not mentioned. None if not applicable.")

class SiteCondition(BaseModel): 
    inland_urban: bool
    inland_mountain: bool
    coastal: bool
    special_site: Optional[SpecialSite]

class SpatiotemporalCharacteristics(BaseModel):
    time_scale: TimeScale  # 时间尺度，定义灾害发生的时间跨度
    spatial_scale: SpatialScale  # 空间尺度，定义关注的空间范围
    site_condition: Optional[SiteCondition] = Field(description="Applicable when considering specific site conditions at the bridge location.")  # 场地条件，适用于考虑桥位处的特定场地情况

class BasicResearch(BaseModel):
    theoretical_framework_development: bool
    new_model_development: bool
    
class AppliedResearch(BaseModel):
    develop_new_methods_or_technologies: bool
    improve_existing_method: bool

class ResearchPurpose(BaseModel):
    basic_research: BasicResearch
    applied_research: AppliedResearch

class ExperimentalMethod(BaseModel):
    quasi_static_test: bool
    real_time_pseudo_dynamic_test: bool
    shaking_table_test: bool

class StructuralSimulation(BaseModel):
    simulate_structural_stiffness: bool
    element_type: Literal["Beam", "Fiber", "Solid"]
    simulate_site_conditions: bool
    site_structure_interaction: Optional[Literal["Separate", "Integrated"]] = Field(description="Applicable when simulates site.")
    spatial_scope_determination: Optional[str] = Field(description="How the spatial scope of the simulated site conditions is determined. Applicable when simulates site.")
    simulate_material_deterioration: bool
    decay_type: Optional[Literal["Stiffness degradation", "Detailed simulation"]] = Field(description="Applicable when simulates material deterioration.")
    simulate_structural_aerodynamics: bool
    areodynamic_range: Optional[Literal["Important components", "Entire bridge"]] = Field(description="Applicable when simulates structural aerodynamics.")
    others: Optional[str] = Field(description="Other aspects of structural simulation not mentioned, like crash, friction, etc.")

class DisasterSimulation(BaseModel):
    hazard: Hazard
    external_load: bool = Field(description="Consider this hazard by adding external load to structure.")
    modal_refinement: bool = Field(description="Consider this hazard by modal refinement. Such as Simulate Structural Component/Construction, Simulate Solid Sites, Simulate Solid Interfaces,Simulate Fluid-Solid Coupling, etc.")

class ComputationalSimulation(BaseModel):
    structure: StructuralSimulation
    disaster: list[DisasterSimulation]

class ResearchMethod(BaseModel):
    experiment: Optional[ExperimentalMethod]
    computational_simulation: Optional[ComputationalSimulation]

# PBEE: Performance-Based Earthquake Engineering
class Multi_Hazard_Hazard_Analysis(BaseModel):
    hazard_identification: bool
    comprehending_the_interactions: bool
    quantifying_probability_of_hazards: bool

class Multi_Hazard_Damage_Analysis(BaseModel):
    demand_or_capacity: Literal["Demand", "Capacity"]
    vulnerable_components: Optional[list[str]]
    damage_index: Optional[list[str]]
    failure_mode: Optional[list[str]]

class RiskWorkflow(BaseModel):
    HAZUS: bool
    OpenQuake: bool
    SimCenter: bool
    IN_CORE: bool
    other: Optional[str] = Field(description="Other risk workflow not mentioned.")

class Multi_Hazard_Risk_Analysis(BaseModel):
    IM: list[str] = Field(description="intensity measure for fragility/vulnerability/risk analysis.")
    EDP: list[str] = Field(description="Engineering demand parameters for fragility/vulnerability/risk analysis.")
    fragility_development_method: Optional[str] = Field(description="Applicable when developing fragility curves. Methods like IDA(incremental dynamic analysis),MSA(multi-strip analysis),CSM(capacity spectrum method),Cloud analysis,Surrogate modeling, etc.")
    workflow: Optional[RiskWorkflow]
    
class Multi_Hazard_Loss_Analysis(BaseModel):
    # 是否考虑直接损失，如维修、更换成本、受损结构碎片及人员伤亡
    direct_loss: bool = Field(description="Whether direct losses such as repair/replacement costs, debris, and casualties are considered.")

    # 是否考虑间接损失，如结构功能的占用、中断或丧失带来的累积影响
    indirect_loss: bool = Field(description="Whether indirect losses such as the accumulation of impacts from the interruption, loss, or occupation of structure functionality are considered.")

    # 是否对生命线基础设施网络及其相互依赖性进行建模
    lifeline_infrastructure_modeling: bool = Field(description="Whether modeling of lifeline infrastructure networks and their interdependencies is included.")

    # 是否对损失不确定性及传播进行建模
    loss_uncertainty_modeling: bool = Field(description="Whether the uncertainty of losses and their propagation is modeled.")

    # 是否提供快速且精准的损失估算方法
    rapid_loss_estimation: bool = Field(description="Whether a rapid and accurate loss estimation method is provided.")

class ResilienceGoal(BaseModel):
    # 材料性能修复与提升
    material_performance: bool = Field(description="Restoration and enhancement of material performance.")

    # 单一结构韧性
    structural_resilience: bool = Field(description="Resilience modeling of individual structures.")

    # 区域系统韧性
    regional_resilience: bool = Field(description="Resilience planning for regional infrastructure systems.")

class RiskSourceAndIndex(BaseModel):
    source: str
    performance_index: list[str]

class ResilienceQuantification(BaseModel):
    # 风险源与性能指标列表
    risk_sources_and_performance_index: Optional[list[RiskSourceAndIndex]]

    # 是否使用定量韧性指标
    quantitative: bool = Field(description="Whether resilience is measured quantitatively.")

    # 是否使用定性韧性指标
    qualitative: bool = Field(description="Whether resilience is measured qualitatively.")

class ResiliencePromotion(BaseModel):
    # 防灾：准备与规划
    preparedness: bool = Field(description="Prepare and plan for disasters.")

    # 减灾/抗灾：吸收或预防灾害
    mitigation: bool = Field(description="Absorb or prevent disaster impacts.")

    # 灾后恢复：从灾害中恢复
    recovery: bool = Field(description="Recover from disasters.")

class Multi_Hazard_Resilience_Analysis(BaseModel):
    goal: ResilienceGoal
    quantification: ResilienceQuantification
    measures:Optional[ResiliencePromotion] = Field(description="Applicable when discussing resilience promotion measures.")
    

class Topic(BaseModel):
    hazard: Optional[Multi_Hazard_Hazard_Analysis] = Field(description="Applicable when considers simulation of multiple hazards itself")
    damage: Optional[Multi_Hazard_Damage_Analysis] = Field(description="Applicable when considers joint effects of structural demand and capacity under multiple hazards")
    risk: Optional[Multi_Hazard_Risk_Analysis] = Field(description="Applicable when considers the probability/risk of structure damage due to multiple hazards")
    loss: Optional[Multi_Hazard_Loss_Analysis] = Field(description="Applicable when considers the direct and indirect losses and cost due to multiple hazards")
    resilience: Optional[Multi_Hazard_Resilience_Analysis] = Field(description="Applicable when considers multi-hazard resilience analysis or promotion")

class ArticleSummary(BaseModel):
    basic_info: BasicInfo
    research_subject: ResearchSubject
    spatialtemporal_characteristics: SpatiotemporalCharacteristics
    purpose: ResearchPurpose
    method: ResearchMethod
    topic: Topic

def get_article_content(path):
    content = []
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content
        
def get_article_summary(text: str, SummaryPrompt:str, MODEL:str = Literal["gpt-4o-2024-08-06","gpt-4o-mini-2024-07-18"]):
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SummaryPrompt},
            {"role": "user", "content": "Please Summarize the Atticle below in given format:\n"+text}
        ],
        response_format=ArticleSummary,
    )

    return completion.choices[0].message.parsed

def extract_title_url_from_context(context: str, image_url: str) -> tuple[str, str]:
    class Picture(BaseModel):
        whole_fig_name: str
        url: str
                
    # Call GPT to get complete image description and URL
    prompt = f"""
    Based on the following context, please provide the figure URL(e.g. 'images/picture.jpg') and full title(e.g. 'Fig. X. Flowchart for something'  ):
    Image URL: {image_url}
    Image context:
    {context}
    """
    extraction = client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18", # save money with gpt-4o-mini
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
        response_format=Picture,
    )
    extraction_result = extraction.choices[0].message.parsed
    title = extraction_result.whole_fig_name
    image_url = extraction_result.url
    return title,image_url

SummaryPrompt = """
    Analyze the provided PDF document on multi-hazard and bridge engineering to extract and analyze key insights. 
    Perform an in-depth reading, focusing on the following aspects:\n\n
    1. Whether multi-hazard risks need to be considered and, if so, how they should be accounted for.\n
    2. Identify if the document discusses vulnerable components and possible failure modes of bridge structures undervarious hazards.\n
    3. Provide an overview of the principles or recommended methods for conducting hazard simulations.
    """

RolePrompt = """
    Role: You are a professional scientific literature image analyst. Your task is to provide a clear and concise analysis of images in scientific literature.
    1.Briefly identify the image type (e.g., photo, chart, microscopy, etc.).
    2.Summarize the main content or key features of the image.
    3.Highlight any important information in the image that may be useful for future research.
    4.Suggest a possible scientific hypothesis or conclusion based on the image and content.
    5.Evaluate the image's significance in supporting the research or findings.
    
    Guidelines:
    Use concise, objective language in your analysis, and ensure your comments are based on information visible in the image.
    If the image lacks sufficient detail to make a clear conclusion, note that additional context or background is needed.
    """

if __name__ == "__main__":
    MODEL="gpt-4o-2024-08-06"

    articles = [
        Path("./articles/Wu et al_2024_Multihazard resilience and economic loss evaluation method for cable-stayed.md"),    
        # Path("./articles/Carey et al_2019_Multihazard Earthquake and Tsunami Effects on Soil-Foundation-Bridge Systems.md"),
    ]
    
    from GeneralAgent import Agent
    import re
    
    for article in articles:
        logger.opt(colors=True).info(f"Processing article: <yellow>{article.stem}</yellow>")
        content = get_article_content(article)
        
        # 提取图片描述和URL的正则表达式
        image_pattern = r'!\[(.*?)\]\((.*?)\)'
        
        # 提取所有图片描述和URL
        image_matches = re.findall(image_pattern, content)
        # 更新的content
        updated_content = content
        
        for description, image_url in image_matches:
            # 获取图片前3句话和后5句话
            image_index = content.index(image_url)
            before_image = content[:image_index].split('.')[-3:]
            after_image = content[image_index:].split('.')[1:6]
            context = '.'.join(['Before Figure loc:'] + before_image +   ['Figure loc:'] + [description] + ['After Figure loc:'] + after_image)

            # 检查上下文中是否存在"Fig.X"或"fig.X"格式的字段，包括点号前后有无空格的情况
            fig_pattern = r'[Ff]ig\s*\.?\s*\d+\.'
            fig_match = re.search(fig_pattern, context)
            if fig_match:
                fig_reference = fig_match.group()
                # 在全文中搜索该字段
                full_context_match = re.search(f'(.{{0,300}}{re.escape(fig_reference)}.{{0,300}})', content)
                if full_context_match:
                    mentionedcontext = full_context_match.group(1)

            # 清理上下文，确保句子完整
            mentionedcontext = re.sub(r'^\S+\s', '', mentionedcontext)  # 移除开头的不完整句子
            mentionedcontext = re.sub(r'\s\S+$', '', mentionedcontext)  # 移除结尾的不完整句子
            
            title, new_image_url = extract_title_url_from_context(context=context,image_url=image_url)
            imagepath = article.parent / new_image_url
            
            agent = Agent(role=RolePrompt, api_key=API_KEY, base_url=BASE_URL, disable_python_run=True, model=MODEL)
            vision_description = agent.user_input([f'Describe what can you see and refer from the image? \
                This figure is mentioned in :\n\n{mentionedcontext}\n\
                and this figure has a context:{context}\n\
                Please conduct your analysis using objective, professional language, and ensure your comments are based on information visible in the image.',
                {'image': str(imagepath.absolute())}])
            # 去除过多的空行并放入引用块
            vision_description = "\n> " + vision_description.replace('\n+', '\n').replace('\n', '\n> ')
            # 也可以放入html的注释块
            # vision_description = f'<!-- {vision_description.replace('\n+', '\n')} -->'
            
            logger.opt(colors=True).success(f"<yellow>{title}</yellow> at path:{str(imagepath.relative_to(Path('.')))} description get!")
            logger.info(f"图片分析结果:\n{vision_description}")
            
            # 更新图片描述
            old_image_tag = f'![{description}]({image_url})'
            new_image_tag = f'![{title}]({image_url}){vision_description}'
            updated_content = updated_content.replace(old_image_tag, new_image_tag)
    
    # 将更新后的内容写回文件
    with open(article, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.opt(colors=True).success(f"已更新 {article} 中的图片描述")
             
    for article in articles:
        content = get_article_content(article)
        summary = get_article_summary(content, SummaryPrompt, MODEL)
        
        if hasattr(summary, 'refusal'):
            logger.opt(colors=True).error(f"文章 <yellow>{article}</yellow> 被拒绝回答")
            if summary.refusal_details:
                logger.opt(colors=True).error(f"拒绝详情: <red>{summary.refusal}</red>")
            continue
        
        # 将摘要保存为JSON文件
        output_filename = f"./articles/{article.stem}_summary.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(summary.model_dump(), f, ensure_ascii=False, indent=4)
        
        logger.opt(colors=True).success(f"已成功保存结果到 {output_filename}")



