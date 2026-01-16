"""
占卜相关API路由
"""
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field
from typing import List, Optional
from collections import defaultdict
from app.core.processor import output_hexagram_results
from app.core.generator import yarrow_hexagram
from app.core.karma_system import KarmaSystem
from app.services.ai_agent import YiMasterAgent
import random
import time
import asyncio

router = APIRouter()

# 存储每个用户的元气系统（基于用户ID实现用户隔离）
# 使用 defaultdict 自动为新用户创建元气系统
# K=20 标准模式：1分钟内连续算会有痛感，连点3次直接没电，需要休息30秒以上才能恢复常态
# 注意：使用 user_id（IP + User-Agent组合）而不是 client_ip，以区分同网络环境的不同用户
user_karma_systems = defaultdict(
    lambda: KarmaSystem(max_vitality=100.0, base_cost=5.0, penalty_factor=20.0)
)

# 存储每个用户的请求记录（用于API限流）
# 使用 user_id 而不是 client_ip，以区分同网络环境的不同用户
request_records = defaultdict(list)

# 并发控制：限制同时进行的AI调用数量（最多10个）
ai_call_semaphore = asyncio.Semaphore(10)

# 用户级别的锁：防止同一用户的并发请求导致元气重复扣除
from collections import defaultdict as defaultdict_sync
user_locks = defaultdict_sync(lambda: asyncio.Lock())


def cleanup_inactive_users():
    """
    清理不活跃的用户数据
    防止内存泄漏
    """
    current_time = time.time()
    inactive_threshold = 24 * 3600  # 24小时未使用视为不活跃
    
    # 清理 user_karma_systems（超过24小时未使用）
    inactive_user_ids = []
    for user_id, system in list(user_karma_systems.items()):
        # 检查最后活跃时间
        time_since_active = current_time - system.last_active_time
        if time_since_active > inactive_threshold:
            inactive_user_ids.append(user_id)
    
    for user_id in inactive_user_ids:
        del user_karma_systems[user_id]
    
    # 清理 request_records（超过1小时未使用）
    record_threshold = 3600  # 1小时
    inactive_record_user_ids = []
    for user_id, records in list(request_records.items()):
        if records:
            # 获取最近的请求时间
            latest_request = max(records)
            time_since_latest = current_time - latest_request
            if time_since_latest > record_threshold:
                inactive_record_user_ids.append(user_id)
        else:
            # 空记录也清理
            inactive_record_user_ids.append(user_id)
    
    for user_id in inactive_record_user_ids:
        del request_records[user_id]
    
    if inactive_user_ids or inactive_record_user_ids:
        print(f"🧹 清理了 {len(inactive_user_ids)} 个不活跃用户和 {len(inactive_record_user_ids)} 个请求记录")


def get_client_ip(req: Request) -> str:
    """
    获取客户端真实IP地址
    考虑代理和CDN的情况（如Cloudflare）
    """
    # 优先使用 X-Forwarded-For 头（如果有代理）
    forwarded_for = req.headers.get("X-Forwarded-For")
    if forwarded_for:
        # 取第一个IP（原始客户端IP）
        return forwarded_for.split(",")[0].strip()
    
    # 使用 CF-Connecting-IP（Cloudflare）
    cf_ip = req.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()
    
    # 否则使用直接连接的IP
    return req.client.host if req.client else "unknown"


def get_user_id(req: Request) -> str:
    """
    获取用户唯一标识（IP + User-Agent组合）
    用于区分同网络环境下的不同用户
    
    使用IP + User-Agent组合的原因：
    1. 同网络环境（共享公网IP）的用户可以通过User-Agent区分
    2. 不同网络环境的用户通过IP区分
    3. 不需要前端配合，实现简单
    """
    import hashlib
    
    client_ip = get_client_ip(req)
    user_agent = req.headers.get("User-Agent", "unknown")
    
    # 组合IP和User-Agent生成唯一标识
    user_id = hashlib.md5(f"{client_ip}:{user_agent}".encode()).hexdigest()
    return user_id


def check_rate_limit(
    user_id: str, 
    max_requests: int = 10, 
    window_seconds: int = 3600  # 默认改为3600秒（1小时）
) -> tuple[bool, dict]:
    """
    检查是否超过限流
    防止单个用户占用过多资源，影响其他用户
    
    :param user_id: 用户唯一标识（IP + User-Agent组合）
    :param max_requests: 时间窗口内最大请求数
    :param window_seconds: 时间窗口（秒），默认3600秒（1小时）
    :return: (是否允许, 限流信息)
    """
    current_time = time.time()
    
    # 清理过期记录（超过时间窗口的请求）
    request_records[user_id] = [
        req_time for req_time in request_records[user_id]
        if current_time - req_time < window_seconds
    ]
    
    # 检查是否超过限制
    if len(request_records[user_id]) >= max_requests:
        # 计算需要等待的时间
        if request_records[user_id]:
            oldest_request = min(request_records[user_id])
            retry_after = int(window_seconds - (current_time - oldest_request)) + 1
        else:
            retry_after = window_seconds
        
        return False, {
            "max_requests": max_requests,
            "window_seconds": window_seconds,
            "current_requests": len(request_records[user_id]),
            "retry_after": retry_after
        }
    
    # 记录本次请求
    request_records[user_id].append(current_time)
    return True, {}


class SingleLineResponse(BaseModel):
    """单个爻响应模型"""
    value: int = Field(..., description="爻的原始数值：6(老阴), 7(少阳), 8(少阴), 9(老阳)")
    binary: int = Field(..., description="爻的二进制值：0(阴), 1(阳)")
    name: str = Field(..., description="爻的名称：老阴、少阳、少阴、老阳")
    karma_status: Optional[dict] = Field(None, description="元气状态信息")


class DivinationRequest(BaseModel):
    """占卜请求模型"""
    question: str = Field(..., min_length=1, max_length=500, description="用户问题")
    hex_lines: Optional[List[int]] = Field(None, description="六爻数据（可选，如果提供则使用，否则后端生成）")


class HexagramResponse(BaseModel):
    """卦象响应模型"""
    original_name: str
    changed_name: str
    original_binary: List[int]
    changed_binary: List[int]
    original_symbol: str
    changed_symbol: str
    original_nature: str
    changed_nature: str
    original_hexagram: List[int]
    changed_hexagram: List[int]


class HexagramInfoResponse(BaseModel):
    """卦象说明响应模型"""
    composition: str
    meaning: str
    quote: str


class DivinationResponse(BaseModel):
    """占卜完整响应模型"""
    hexagram_data: HexagramResponse
    interpretation: str
    technician_id: int
    original_info: Optional[HexagramInfoResponse] = None
    changed_info: Optional[HexagramInfoResponse] = None
    karma_status: Optional[dict] = Field(None, description="元气状态信息（完成6个爻后统一结算）")


@router.post("/divination/generate-line", response_model=SingleLineResponse)
async def generate_single_line(req: Request, response: Response):
    """
    生成单个爻
    
    使用蓍草法生成一个爻的数值（6,7,8,9）
    所有卦象数据都由后端processor生成，确保数据一致性
    
    注意：生成单个爻时不消耗元气，元气消耗在完成6个爻后统一结算。
    """
    try:
        # 获取用户ID并获取该用户的元气系统
        user_id = get_user_id(req)
        
        # 检查API限流（生成单个爻接口：每小时最多30次请求）
        allowed, limit_info = check_rate_limit(user_id, max_requests=30, window_seconds=3600)
        if not allowed:
            retry_after_minutes = limit_info['retry_after'] // 60
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "请求过于频繁",
                    "message": f"请稍后再试，每小时最多30次请求。请在 {retry_after_minutes} 分钟后重试。",
                    "limit_info": limit_info
                }
            )
        
        karma_system = user_karma_systems[user_id]
        
        # 直接生成爻，不消耗元气
        value = yarrow_hexagram()  # 返回 6, 7, 8, 或 9
        binary = 1 if value in [7, 9] else 0  # 7和9是阳爻(1)，6和8是阴爻(0)
        
        # 生成爻的名称
        name_map = {6: "老阴", 7: "少阳", 8: "少阴", 9: "老阳"}
        name = name_map.get(value, "未知")
        
        # 返回当前元气状态（不消耗）
        karma_status = karma_system.get_status()
        
        return SingleLineResponse(
            value=value,
            binary=binary,
            name=name,
            karma_status=karma_status
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"生成爻失败 - 详细错误:\n{error_trace}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "生成爻失败",
                "message": str(e),
                "hint": "请检查后端日志以获取详细信息"
            }
        )


@router.post("/divination/generate", response_model=HexagramResponse)
async def generate_hexagram():
    """
    生成卦象
    
    返回本卦和变卦的完整信息
    """
    try:
        hexagram_data = output_hexagram_results()
        return HexagramResponse(**hexagram_data)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"生成卦象失败 - 详细错误:\n{error_trace}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "生成卦象失败",
                "message": str(e),
                "hint": "请检查后端日志以获取详细信息"
            }
        )


@router.post("/divination/interpret", response_model=DivinationResponse)
async def interpret_divination(request: DivinationRequest, req: Request, response: Response):
    """
    AI解读占卜结果
    
    接收用户问题和卦象数据，返回AI解读结果
    
    采用三阶段模式结算元气：
    1. 验资（preview）：检查元气是否足够，不扣费
    2. 生成：执行卦象生成和AI解读逻辑
    3. 结算（commit）：生成成功后扣除元气
    
    如果生成失败，不会扣除元气，保证公平交易。
    """
    try:
        # 获取用户ID并获取该用户的元气系统
        user_id = get_user_id(req)
        
        # 设置Cookie，保持用户ID的持久性（30天有效期）
        response.set_cookie(
            key="user_id",
            value=user_id,
            max_age=30 * 24 * 3600,  # 30天
            httponly=True,  # 防止XSS攻击
            samesite="lax"  # CSRF保护
        )
        
        # 使用用户级别的锁，防止并发请求导致元气重复扣除
        async with user_locks[user_id]:
            # 检查API限流（占卜解读接口：每小时最多10次请求）
            allowed, limit_info = check_rate_limit(user_id, max_requests=10, window_seconds=3600)
            if not allowed:
                retry_after_minutes = limit_info['retry_after'] // 60
                raise HTTPException(
                    status_code=429,  # Too Many Requests
                    detail={
                        "error": "请求过于频繁",
                        "message": f"请稍后再试，每小时最多10次请求。请在 {retry_after_minutes} 分钟后重试。",
                        "limit_info": limit_info
                    }
                )
            
            karma_system = user_karma_systems[user_id]
            
            # 更新最后活跃时间（用于内存清理）
            karma_system.last_active_time = time.time()
            
            # 更新元气值（考虑衰减和恢复）
            karma_system.update_vitality()
            
            # 检查元气是否足够（元气为0时不能使用）
            if karma_system.current_vitality <= 0:
                raise HTTPException(
                    status_code=429,  # Too Many Requests
                    detail={
                        "error": "元气不足",
                        "message": "元神枯竭，无法窥探天机。请稍作休息，或考虑充值恢复元气。",
                        "current_vitality": karma_system.current_vitality,
                        "required_cost": 0,
                        "karma_status": karma_system.get_status()
                    }
                )
            
            # --- 阶段一：验资（Pre-check）---
            # 这一步不扣钱，只是看用户有没有资格完成整个占卜
            preview = karma_system.calculate_cost_preview()
            
            if not preview["can_afford"]:
                # 还没生成就没钱了，直接报错返回，不扣任何东西
                raise HTTPException(
                    status_code=429,  # Too Many Requests
                    detail={
                        "error": "元气不足",
                        "message": "元神枯竭，无法窥探天机",
                        "current_vitality": preview["current_vitality"],
                        "required_cost": preview["estimated_cost"],
                        "karma_status": karma_system.get_status()
                    }
                )
            
            # 记录预计消耗（用于后续结算）
            estimated_cost = preview["estimated_cost"]
        
            # --- 阶段二：生成卦象和AI解读（Business Logic）---
            # 如果这里报错了，代码会中断，永远不会走到阶段三，所以用户不会亏钱
            
            # 1. 生成或使用提供的卦象数据
            # 如果前端提供了六爻数据（6,7,8,9数组），使用这些值生成卦象
            # 所有卦象数据都由后端processor生成，确保数据一致性
            if request.hex_lines and len(request.hex_lines) == 6:
                # 验证所有值都在有效范围内（6,7,8,9）
                if all(v in [6, 7, 8, 9] for v in request.hex_lines):
                    hexagram_data = output_hexagram_results(original_hexagram_values=request.hex_lines)
                else:
                    # 如果值无效，生成新的卦象
                    hexagram_data = output_hexagram_results()
            else:
                # 后端生成卦象
                hexagram_data = output_hexagram_results()
            
            # 2. 初始化AI代理
            try:
                agent = YiMasterAgent()
            except ValueError as e:
                # API_KEY 配置错误
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "AI服务配置错误",
                        "message": str(e),
                        "hint": "请在 backend 目录下创建 .env 文件，并添加 DEEPSEEK_API_KEY=your_api_key"
                    }
                )
            except Exception as e:
                # 其他初始化错误
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "AI服务初始化失败",
                        "message": str(e),
                        "hint": "请检查后端日志以获取详细信息"
                    }
                )
            
            # 3. 调用AI进行解读（使用异步执行，避免阻塞其他请求）
            # 将同步的AI调用放到线程池中执行，不阻塞事件循环
            # 使用信号量限制并发数量，防止资源耗尽
            async with ai_call_semaphore:
                interpretation = await asyncio.to_thread(
                    agent.consult,
                    hexagram_data,
                    request.question,
                    stream_mode=False
                )
            
            # 4. 生成随机技师ID
            technician_id = random.randint(1, 100)
            
            # 5. 获取卦象说明信息（本卦和变卦）
            # 使用异步方式，避免AI调用阻塞主流程
            # 如果AI调用失败，返回None，前端会使用默认值
            original_info = None
            changed_info = None
            
            try:
                # 尝试获取本卦信息（使用异步执行，避免阻塞）
                # 使用信号量限制并发数量
                try:
                    async with ai_call_semaphore:
                        original_info_dict = await asyncio.to_thread(
                            agent.get_hexagram_info,
                            hexagram_data['original_name'],
                            hexagram_data['original_nature']
                        )
                    if original_info_dict and isinstance(original_info_dict, dict):
                        original_info = HexagramInfoResponse(**original_info_dict)
                except Exception as e:
                    print(f"警告: 获取本卦信息失败: {str(e)}")
                    # 使用默认值，不阻塞主流程
                    original_info = None
                
                # 尝试获取变卦信息（使用异步执行，避免阻塞）
                # 使用信号量限制并发数量
                try:
                    async with ai_call_semaphore:
                        changed_info_dict = await asyncio.to_thread(
                            agent.get_hexagram_info,
                            hexagram_data['changed_name'],
                            hexagram_data['changed_nature']
                        )
                    if changed_info_dict and isinstance(changed_info_dict, dict):
                        changed_info = HexagramInfoResponse(**changed_info_dict)
                except Exception as e:
                    print(f"警告: 获取变卦信息失败: {str(e)}")
                    # 使用默认值，不阻塞主流程
                    changed_info = None
            except Exception as e:
                # 如果整体获取失败，不影响主流程
                print(f"警告: 获取卦象说明信息失败: {str(e)}")
                original_info = None
                changed_info = None
            
            # --- 阶段三：结算扣费（Commit）---
            # AI调用完成后，重新更新元气（因为可能在AI调用期间恢复了）
            karma_system.update_vitality()
            
            # 重新计算消耗（因为元气可能已恢复）
            final_preview = karma_system.calculate_cost_preview()
            
            # 使用实际消耗值（取验资时的消耗和当前计算的消耗的较小值，防止因恢复导致消耗增加）
            actual_cost = min(estimated_cost, final_preview["estimated_cost"])
            
            # 确保元气足够支付实际消耗
            if karma_system.current_vitality < actual_cost:
                # 如果元气不足，使用当前可用的元气值（但不能超过预计消耗）
                actual_cost = min(actual_cost, karma_system.current_vitality)
            
            # 扣除元气
            commit_success = karma_system.commit_transaction(actual_cost)
            
            if not commit_success:
                # 理论上不应该发生（因为已经验资过了），但防止并发问题
                raise HTTPException(
                    status_code=500,
                    detail="结算失败，请重试"
                )
            
            # 记录使用（用于计算衰减和恢复）
            karma_system.record_use()
            
            # 构建返回的元气状态信息
            karma_status = {
                "success": True,
                "message": "卦象已成",
                "cost": actual_cost,  # 使用实际消耗值
                "current_vitality": karma_system.current_vitality,
                "max_vitality": karma_system.max_vitality,
                "percentage": round((karma_system.current_vitality / karma_system.max_vitality) * 100, 1),
                "time_since_last": preview["delta_t"],
                "is_glitch": preview["is_glitch"],
                "warning_level": preview["warning_level"]
            }
        
        return DivinationResponse(
            hexagram_data=HexagramResponse(**hexagram_data),
            interpretation=interpretation,
            technician_id=technician_id,
            original_info=original_info,
            changed_info=changed_info,
            karma_status=karma_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"占卜解读失败 - 详细错误:\n{error_trace}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "占卜解读失败",
                "message": str(e),
                "hint": "请检查后端日志以获取详细信息"
            }
        )


@router.get("/divination/karma-status")
async def get_karma_status(req: Request, response: Response):
    """
    获取当前元气状态（不消耗元气）
    """
    # 获取用户ID并获取该用户的元气系统
    user_id = get_user_id(req)
    karma_system = user_karma_systems[user_id]
    
    return karma_system.get_status()


@router.post("/divination/recharge")
async def recharge_karma(req: Request, response: Response):
    """
    充能接口（付费恢复元气）
    模拟付费流程，实际应该对接支付系统
    """
    # 获取用户ID并获取该用户的元气系统
    user_id = get_user_id(req)
    
    # 检查API限流（充能接口：每小时最多5次请求，防止滥用）
    allowed, limit_info = check_rate_limit(user_id, max_requests=5, window_seconds=3600)
    if not allowed:
        retry_after_minutes = limit_info['retry_after'] // 60
        raise HTTPException(
            status_code=429,
            detail={
                "error": "请求过于频繁",
                "message": f"请稍后再试，每小时最多5次充能。请在 {retry_after_minutes} 分钟后重试。",
                "limit_info": limit_info
            }
        )
    
    karma_system = user_karma_systems[user_id]
    
    # 模拟付费成功，恢复元气到满值
    karma_system.current_vitality = karma_system.max_vitality
    karma_system.last_recovery_time = time.time()
    
    return {
        "success": True,
        "message": "元气已恢复",
        "current_vitality": karma_system.current_vitality,
        "karma_status": karma_system.get_status()
    }
