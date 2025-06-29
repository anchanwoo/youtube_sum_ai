import time
import random
from concurrent.futures import ThreadPoolExecutor

def simulate_api_call(task_name, delay_range=(1.0, 3.0)):
    """실제 API 호출 지연 시뮬레이션"""
    delay = random.uniform(*delay_range)
    print(f"   🔄 {task_name} 처리 중... ({delay:.1f}초)")
    time.sleep(delay)
    return f"{task_name} 완료"

def sequential_processing_realistic():
    """현실적인 순차 처리 (실제 API 지연 포함)"""
    print("🐌 순차 처리 시작 (실제 API 지연 시뮬레이션)")
    start_time = time.time()
    
    topics = ["AI", "로봇", "미래", "교육", "환경"]
    results = []
    
    for i, topic in enumerate(topics, 1):
        print(f"\n🎯 주제 {i}: {topic}")
        
        # Q&A 생성 (각각 1-3초 소요)
        for j in range(3):
            result = simulate_api_call(f"{topic} Q&A #{j+1} 생성", (1.0, 3.0))
            results.append(result)
        
        # 친화적 변환 (각각 0.5-1.5초 소요)
        for j in range(3):
            simulate_api_call(f"{topic} Q&A #{j+1} 질문 변환", (0.5, 1.5))
            simulate_api_call(f"{topic} Q&A #{j+1} 답변 변환", (0.5, 1.5))
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n📊 순차 처리 결과:")
    print(f"   ⏱️  총 처리 시간: {total_time:.1f}초")
    print(f"   📞 총 API 호출: {len(topics) * 3 + len(topics) * 3 * 2}회")
    print(f"   📈 평균 호출당 시간: {total_time / (len(topics) * 9):.1f}초")
    
    return total_time

def mapreduce_processing_realistic():
    """현실적인 MapReduce 처리 (병렬 처리)"""
    print("🚀 MapReduce 처리 시작 (병렬 처리)")
    start_time = time.time()
    
    topics = ["AI", "로봇", "미래", "교육", "환경"]
    
    # Map Phase 1: Q&A 생성 (병렬)
    print("\n🗺️  Map Phase 1: Q&A 생성 (5개 주제 동시 처리)")
    
    def generate_qa_batch(topic):
        qa_results = []
        for j in range(3):
            result = simulate_api_call(f"{topic} Q&A #{j+1} 생성", (1.0, 3.0))
            qa_results.append(result)
        return qa_results
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        qa_results = list(executor.map(generate_qa_batch, topics))
    
    map1_time = time.time()
    print(f"\n✅ Map Phase 1 완료: {map1_time - start_time:.1f}초")
    
    # Map Phase 2: 친화적 변환 (병렬)
    print("\n🗺️  Map Phase 2: 친화적 변환 (15개 Q&A 동시 처리)")
    
    all_qa_items = []
    for i, topic in enumerate(topics):
        for j in range(3):
            all_qa_items.append(f"{topic} Q&A #{j+1}")
    
    def convert_qa_batch(qa_item):
        simulate_api_call(f"{qa_item} 질문 변환", (0.5, 1.5))
        simulate_api_call(f"{qa_item} 답변 변환", (0.5, 1.5))
        return f"{qa_item} 변환 완료"
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        conversion_results = list(executor.map(convert_qa_batch, all_qa_items))
    
    end_time = time.time()
    total_time = end_time - start_time
    map2_time = end_time - map1_time
    
    print(f"\n✅ Map Phase 2 완료: {map2_time:.1f}초")
    print(f"\n📊 MapReduce 처리 결과:")
    print(f"   ⏱️  총 처리 시간: {total_time:.1f}초")
    print(f"   📞 총 API 호출: {len(topics) * 3 + len(topics) * 3 * 2}회")
    print(f"   📈 평균 호출당 시간: {total_time / (len(topics) * 9):.1f}초")
    
    return total_time

def demonstrate_gpu_analogy():
    """GPU vs MapReduce 시각적 비교"""
    print("\n" + "=" * 60)
    print("🎮 GPU vs MapReduce 병렬 처리 원리 비교")
    print("=" * 60)
    
    print("\n🖥️ GPU 병렬 처리 (예: 1920x1080 이미지)")
    print("   📐 총 픽셀: 2,073,600개")
    print("   🔢 GPU 코어: 2,560개 (예: RTX 3070)")
    print("   ⚡ 처리 방식:")
    print("      Core 1: pixel(0,0) 처리")
    print("      Core 2: pixel(0,1) 처리") 
    print("      Core 3: pixel(0,2) 처리")
    print("      ...")
    print("      Core 2560: pixel(1,511) 처리")
    print("   🚀 결과: 모든 픽셀을 동시에 처리!")
    
    print("\n🤖 MapReduce 병렬 처리 (YouTube 요약)")
    print("   📝 총 작업: 45개 API 호출")
    print("   🧵 스레드: 15개 (예: ThreadPoolExecutor)")
    print("   ⚡ 처리 방식:")
    print("      Thread 1: 'AI' Q&A #1 생성")
    print("      Thread 2: '로봇' Q&A #1 생성")
    print("      Thread 3: '미래' Q&A #1 생성")
    print("      ...")
    print("      Thread 15: '환경' 변환 처리")
    print("   🚀 결과: 여러 작업을 동시에 처리!")

def analyze_api_costs():
    """API 비용 상세 분석"""
    print("\n" + "=" * 60)
    print("💰 API 비용 및 효율성 분석")
    print("=" * 60)
    
    # 기본 설정
    topics = 5
    qa_per_topic = 3
    cost_per_call = 0.02  # $0.02 per API call
    
    # 비용 계산
    qa_generation_calls = topics * qa_per_topic  # 15회
    conversion_calls = topics * qa_per_topic * 2  # 30회 (질문+답변)
    total_calls = qa_generation_calls + conversion_calls  # 45회
    total_cost = total_calls * cost_per_call
    
    print(f"\n📊 기본 비용 구조:")
    print(f"   🎯 주제 수: {topics}개")
    print(f"   ❓ 주제당 Q&A: {qa_per_topic}개")
    print(f"   🔄 변환 작업: 질문 + 답변 = 2배")
    print(f"   📞 총 API 호출: {total_calls}회")
    print(f"   💵 호출당 비용: ${cost_per_call}")
    print(f"   💰 총 비용: ${total_cost:.2f}")
    
    print(f"\n🔍 MapReduce vs 순차 처리 비용 비교:")
    print(f"   ✅ 직접적 API 비용: 동일 (${total_cost:.2f})")
    print(f"   📈 하지만 간접적 효과:")
    
    # 시간 비용 계산
    dev_hourly_rate = 50  # $50/hour
    sequential_time = 35  # 예상 35초
    mapreduce_time = 8   # 예상 8초
    time_saved = sequential_time - mapreduce_time
    
    tests_per_hour_seq = 3600 / sequential_time
    tests_per_hour_mr = 3600 / mapreduce_time
    productivity_increase = tests_per_hour_mr / tests_per_hour_seq
    
    print(f"      ⏱️  시간 절약: {time_saved}초 ({((time_saved/sequential_time)*100):.0f}% 단축)")
    print(f"      🔄 시간당 테스트: {tests_per_hour_seq:.0f}회 → {tests_per_hour_mr:.0f}회")
    print(f"      📈 생산성 증대: {productivity_increase:.1f}배")
    
    # 실패 처리 비용
    print(f"\n🚨 실패 처리 시나리오:")
    print(f"   순차 처리: 4번째 실패 시 전체 재시작")
    print(f"   - 실패 전 호출: 12회 (무효)")
    print(f"   - 재시작 호출: 45회")
    print(f"   - 총 비용: ${(12 + 45) * cost_per_call:.2f}")
    print(f"   ")
    print(f"   MapReduce: 개별 재시도")
    print(f"   - 실패 호출: 1회만 재시도")
    print(f"   - 총 비용: ${(45 + 1) * cost_per_call:.2f}")
    print(f"   💰 절약: ${((12 + 45) - (45 + 1)) * cost_per_call:.2f} (19% 절약)")

def main():
    """메인 실행 함수"""
    print("🔥 현실적인 MapReduce vs 순차 처리 성능 비교")
    print("=" * 60)
    
    # 순차 처리 테스트
    seq_time = sequential_processing_realistic()
    
    print("\n" + "-" * 40 + "\n")
    
    # MapReduce 처리 테스트  
    mr_time = mapreduce_processing_realistic()
    
    # 결과 분석
    speedup = seq_time / mr_time if mr_time > 0 else 1
    time_saved = seq_time - mr_time
    improvement_percent = (time_saved / seq_time) * 100
    
    print("\n" + "=" * 60)
    print("🎯 성능 비교 최종 결과")
    print("=" * 60)
    print(f"   🐌 순차 처리: {seq_time:.1f}초")
    print(f"   🚀 MapReduce: {mr_time:.1f}초")
    print(f"   ⚡ 성능 향상: {speedup:.1f}배 빨라짐")
    print(f"   📉 시간 단축: {improvement_percent:.0f}% 개선")
    print(f"   💾 절약 시간: {time_saved:.1f}초")
    
    # 추가 분석
    demonstrate_gpu_analogy()
    analyze_api_costs()
    
    print(f"\n🏆 최종 결론:")
    print(f"   🎮 GPU처럼: 병렬 처리로 {speedup:.1f}배 성능 향상")
    print(f"   💰 비용: 직접 절약 없지만 생산성 크게 증대")
    print(f"   🛡️  안정성: 실패 시 개별 재시도로 복구력 향상")
    print(f"   📈 확장성: 주제 수 증가해도 처리 시간 비례하지 않음")

if __name__ == "__main__":
    main() 