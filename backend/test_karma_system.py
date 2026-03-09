from app.core import karma_system


def test_calculate_cost_preview_first_call_is_affordable_and_normal():
    system = karma_system.KarmaSystem(base_cost=5.0, penalty_factor=20.0)

    preview = system.calculate_cost_preview()

    assert preview["can_afford"] is True
    assert preview["estimated_cost"] == 5.0
    assert preview["delta_t"] == 999999
    assert preview["warning_level"] == "NORMAL"
    assert preview["is_glitch"] is False


def test_calculate_cost_preview_marks_danger_and_unaffordable(monkeypatch):
    now = 1_000.0
    monkeypatch.setattr(karma_system.time, "time", lambda: now)
    system = karma_system.KarmaSystem(max_vitality=100.0, base_cost=5.0, penalty_factor=20.0)
    system.current_vitality = 8.0
    system.last_cast_time = now - 10

    preview = system.calculate_cost_preview()

    assert preview["estimated_cost"] == 15.0
    assert preview["can_afford"] is False
    assert preview["warning_level"] == "DANGER"
    assert preview["is_glitch"] is True


def test_commit_transaction_false_and_recharge_caps_at_max():
    system = karma_system.KarmaSystem(max_vitality=100.0)
    system.current_vitality = 3.0

    assert system.commit_transaction(5.0) is False
    assert system.current_vitality == 3.0

    system.current_vitality = 60.0
    assert system.recharge(50.0) == 100.0


def test_activity_factor_changes_by_idle_window():
    system = karma_system.KarmaSystem()
    now = 5_000.0

    system.last_active_time = now - 60
    assert system._get_activity_factor(now) == 1.0

    system.last_active_time = now - 600
    assert system._get_activity_factor(now) == 0.5

    system.last_active_time = now - 2_500
    assert system._get_activity_factor(now) == 0.2

    system.last_active_time = now - 4_000
    assert system._get_activity_factor(now) == 0.0


def test_update_vitality_and_record_use(monkeypatch):
    now = 10_000.0
    monkeypatch.setattr(karma_system.time, "time", lambda: now)
    system = karma_system.KarmaSystem(max_vitality=100.0)
    system.current_vitality = 50.0
    system.total_uses = 10
    system.last_active_time = now - 60
    system.last_recovery_time = now - 3_600

    status = system.update_vitality()

    assert status["decay"] > 0
    assert status["recovery"] > status["decay"]
    assert system.current_vitality > 50.0

    system.record_use()
    assert system.total_uses == 11
    assert system.last_active_time == now
