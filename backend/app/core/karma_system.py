"""
赛博因果系统（KarmaSystem）
管理元气消耗，防止频繁算卦导致系统过载
采用三阶段模式：验资 -> 生成 -> 结算
"""
import time
import math


class KarmaSystem:
    def __init__(self, max_vitality=100.0, base_cost=5.0, penalty_factor=20.0):
        """
        初始化赛博因果系统
        :param max_vitality: 最大元气值 (默认 100)
        :param base_cost: 每次算卦的基础消耗 (默认 5%)
        :param penalty_factor: 惩罚系数 (K值). 推荐设为 20（标准模式）
                               K值越大，冷却惩罚越重。
                               例如 K=20，意味着间隔 20秒 时，消耗翻倍。
        """
        self.max_vitality = max_vitality
        self.current_vitality = max_vitality
        self.last_cast_time = 0  # 上次算卦的时间戳
        self.last_recovery_time = time.time()  # 上次恢复的时间戳
        self.base_cost = base_cost
        self.penalty_factor = penalty_factor  # 推荐 K=20（标准模式）
        
        # 衰减和恢复相关
        self.total_uses = 0  # 总使用次数
        self.active_periods = []  # 活跃时间段列表 [(start_time, end_time), ...]
        self.last_active_time = time.time()  # 上次活跃时间

    def calculate_cost_preview(self):
        """
        阶段一：验资（Pre-check）
        只计算如果不现在算卦，需要消耗多少，但不扣费，也不更新时间。
        用于在生成卦象前检查用户是否有足够的元气。
        
        Returns:
            dict: 包含验资结果的字典
                - can_afford: 是否有足够的元气
                - estimated_cost: 预计消耗
                - current_vitality: 当前元气值
                - is_glitch: 是否过热（消耗超过基础值的2.5倍）
                - delta_t: 距离上次算卦的时间间隔（秒）
                - warning_level: 警告等级（NORMAL/WARNING/DANGER）
        """
        current_time = time.time()
        
        # 1. 计算间隔
        if self.last_cast_time == 0:
            # 第一次运行，视为间隔无限长
            delta_t = 999999
        else:
            delta_t = current_time - self.last_cast_time
        
        # 防止除以零，设置最小间隔为 0.1 秒
        delta_t = max(0.1, delta_t)

        # 2. 计算预计消耗
        # 核心公式：Cost = Base * (1 + K / dt)
        multiplier = 1 + (self.penalty_factor / delta_t)
        estimated_cost = self.base_cost * multiplier
        estimated_cost = round(estimated_cost, 2)

        # 3. 判断是否买得起
        can_afford = self.current_vitality >= estimated_cost
        
        # 4. 判断是否过热（消耗超过基础值的2.5倍）
        is_glitch = estimated_cost > (self.base_cost * 2.5)
        
        # 5. 判断警告等级
        warning_level = self._get_warning_level(estimated_cost)

        return {
            "can_afford": can_afford,
            "estimated_cost": estimated_cost,
            "current_vitality": self.current_vitality,
            "max_vitality": self.max_vitality,
            "percentage": round((self.current_vitality / self.max_vitality) * 100, 1),
            "is_glitch": is_glitch,
            "delta_t": round(delta_t, 1),
            "warning_level": warning_level
        }

    def commit_transaction(self, cost):
        """
        阶段三：结算（Commit）
        只有在卦象生成成功后调用。
        如果生成失败（抛出异常），这个方法不会被调用，用户不会损失元气。
        
        Args:
            cost: 要扣除的元气值（应该使用 preview 时计算的 estimated_cost）
        
        Returns:
            bool: 是否成功扣除元气
        """
        # 再次检查防止并发问题
        if self.current_vitality < cost:
            return False
            
        # 扣除元气
        self.current_vitality -= cost
        # 修正精度（避免出现 99.0000001 的情况）
        self.current_vitality = round(max(0, self.current_vitality), 2)
        
        # 更新时间戳（算卦完成的时间）
        self.last_cast_time = time.time()
        return True

    def _get_warning_level(self, cost):
        """根据消耗判断警告等级，用于前端变色"""
        if cost < self.base_cost * 1.5:
            return "NORMAL"  # 绿色/琥珀色
        elif cost < self.base_cost * 3:
            return "WARNING"  # 黄色
        else:
            return "DANGER"  # 红色闪烁

    def recharge(self, amount=100):
        """
        充能接口（恢复元气）
        """
        self.current_vitality = min(self.max_vitality, self.current_vitality + amount)
        self.current_vitality = round(self.current_vitality, 2)
        return self.current_vitality

    def update_vitality(self):
        """
        更新元气值（考虑衰减和恢复）
        应该在每次请求时调用，自动计算衰减和恢复
        """
        current_time = time.time()
        
        # 1. 计算衰减
        decay = self._calculate_decay(current_time)
        
        # 2. 计算恢复
        recovery = self._calculate_recovery(current_time)
        
        # 3. 更新元气值
        net_change = recovery - decay
        self.current_vitality = max(0, min(self.max_vitality, self.current_vitality + net_change))
        self.current_vitality = round(self.current_vitality, 2)
        
        # 4. 更新恢复时间戳
        self.last_recovery_time = current_time
        
        return {
            "decay": round(decay, 2),
            "recovery": round(recovery, 2),
            "net_change": round(net_change, 2),
            "current_vitality": self.current_vitality
        }
    
    def _calculate_decay(self, current_time):
        """
        计算元气衰减
        根据使用次数和活跃度计算衰减速度
        使用次数越多，衰减越快；活跃度越高，衰减越快
        """
        # 基础衰减率（每小时衰减）
        base_decay_rate = 0.5  # 每小时衰减0.5%
        
        # 使用次数影响（使用越多，衰减越快）
        # 使用对数函数，避免衰减过快
        use_factor = math.log(1 + self.total_uses * 0.1) * 0.3
        
        # 活跃度影响（活跃度越高，衰减越快）
        activity_factor = self._get_activity_factor(current_time) * 0.2
        
        # 总衰减率
        total_decay_rate = base_decay_rate * (1 + use_factor + activity_factor)
        
        # 计算时间差（小时）
        time_diff_hours = (current_time - self.last_recovery_time) / 3600
        
        # 衰减量
        decay = total_decay_rate * time_diff_hours
        
        return decay
    
    def _calculate_recovery(self, current_time):
        """
        计算元气恢复
        根据使用次数和活跃度计算恢复速度
        使用次数越多，恢复越慢；活跃度越低，恢复越快
        """
        # 基础恢复率（每小时恢复）
        base_recovery_rate = 0.3  # 每小时恢复0.3%
        
        # 使用次数影响（使用越多，恢复越慢）
        use_factor = math.log(1 + self.total_uses * 0.1) * -0.2
        
        # 活跃度影响（活跃度越低，恢复越快）
        activity_factor = (1 - self._get_activity_factor(current_time)) * 0.3
        
        # 总恢复率
        total_recovery_rate = base_recovery_rate * (1 + use_factor + activity_factor)
        
        # 计算时间差（小时）
        time_diff_hours = (current_time - self.last_recovery_time) / 3600
        
        # 恢复量
        recovery = total_recovery_rate * time_diff_hours
        
        return recovery
    
    def _get_activity_factor(self, current_time):
        """
        获取活跃度因子（0-1之间）
        根据最近的活动时间计算活跃度
        """
        # 如果最近5分钟内有活动，认为活跃
        time_since_active = current_time - self.last_active_time
        
        if time_since_active < 300:  # 5分钟内
            return 1.0
        elif time_since_active < 1800:  # 30分钟内
            return 0.5
        elif time_since_active < 3600:  # 1小时内
            return 0.2
        else:
            return 0.0
    
    def record_use(self):
        """
        记录使用（增加使用次数和更新活跃时间）
        """
        self.total_uses += 1
        self.last_active_time = time.time()
    
    def get_status(self):
        """
        获取当前状态（不消耗元气，但会更新衰减和恢复）
        """
        # 更新元气值
        self.update_vitality()
        
        return {
            "current_vitality": self.current_vitality,
            "max_vitality": self.max_vitality,
            "percentage": round((self.current_vitality / self.max_vitality) * 100, 1),
            "total_uses": self.total_uses,
            "can_use": self.current_vitality > 0
        }


# --- 本地测试代码 ---
if __name__ == "__main__":
    # 初始化系统（K=20 标准模式）
    system = KarmaSystem(base_cost=5.0, penalty_factor=20.0)

    print(f"--- 系统启动 | 初始元气: {system.current_vitality}% | K=20（标准模式）---")

    # 模拟用户行为
    # 1. 第一次算（正常）
    print("\n[用户]: 点击算卦...")
    preview = system.calculate_cost_preview()
    print(f"  验资结果: 消耗 {preview['estimated_cost']}%, 剩余 {preview['current_vitality']}%")
    if preview['can_afford']:
        system.commit_transaction(preview['estimated_cost'])
        print(f"  结算完成: 剩余 {system.current_vitality}%")
    
    # 2. 疯狂点击（间隔 2秒）
    time.sleep(2) 
    print("\n[用户]: 2秒后急忙再算...")
    preview = system.calculate_cost_preview()
    print(f"  验资结果: 消耗 {preview['estimated_cost']}%, 剩余 {preview['current_vitality']}%")
    if preview['can_afford']:
        system.commit_transaction(preview['estimated_cost'])
        print(f"  结算完成: 剩余 {system.current_vitality}%")
    
    # 3. 极其疯狂点击（间隔 0.5秒）
    time.sleep(0.5)
    print("\n[用户]: 0.5秒后疯狂点击...")
    preview = system.calculate_cost_preview()
    print(f"  验资结果: 消耗 {preview['estimated_cost']}%, 剩余 {preview['current_vitality']}%")
    print(f"  警告等级: {preview['warning_level']}, 过热: {preview['is_glitch']}")
    if preview['can_afford']:
        system.commit_transaction(preview['estimated_cost'])
        print(f"  结算完成: 剩余 {system.current_vitality}%")
    
    # 4. 休息一会儿（间隔 10秒）
    print("\n[用户]: 休息10秒...")
    time.sleep(10)
    preview = system.calculate_cost_preview()
    print(f"  验资结果: 消耗 {preview['estimated_cost']}%, 剩余 {preview['current_vitality']}%")
    if preview['can_afford']:
        system.commit_transaction(preview['estimated_cost'])
        print(f"  结算完成: 剩余 {system.current_vitality}%")
