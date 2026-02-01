---
name: ios-background-task-creator
description: 基于项目中成熟的 AIBackgroundTaskManager 模式，快速创建后台任务，支持持久化、轮询、重试、app生命周期管理等完整功能
---

# iOS 后台任务创建器

## When to Use

Use this skill when you need to:
- 创建异步生成任务（如 AI 图片生成）
- 实现后台数据同步
- 处理需要长时间等待的操作
- 支持 app 退出后任务继续执行
- 创建需要在后台持续运行、支持app重启恢复的长时间任务

## Prerequisites

项目中存在以下参考实现：
- `Features/AIBackgroundTasks/` - 完整的后台任务系统
- `AIBackgroundTaskManager.swift` - 任务管理器
- `JSONAIGenerationRepository.swift` - 任务持久化

## Instructions

### AIBackgroundTaskManager 架构参考

成熟的后台任务应包含：

```
后台任务系统架构：
├── 任务管理器 (Manager)
│   ├── 任务队列管理
│   ├── 并发控制
│   ├── 生命周期管理
│   └── 状态通知
│
├── 任务持久化 (Repository)
│   ├── JSON 文件存储
│   ├── 任务加载/保存
│   └── 状态同步
│
├── 轮询机制
│   ├── 定时轮询
│   ├── 指数退避
│   └── 重试策略
│
└── 生命周期处理
    ├── App 启动恢复
    ├── 后台切换
    └── 任务完成通知
```

### 步骤 1: 定义任务数据模型

创建任务状态和数据结构：

```swift
import Foundation

// ============================================
// 任务状态枚举
// ============================================

enum [TaskName]Status: String, Codable {
    case pending    = "pending"      // 等待执行
    case processing = "processing"   // 执行中
    case completed  = "completed"    // 已完成
    case failed     = "failed"       // 失败
    case cancelled  = "cancelled"    // 已取消
}

// ============================================
// 任务数据模型
// ============================================

struct [TaskName]Job: Codable, Identifiable {
    // MARK: - Properties
    let id: String
    var status: [TaskName]Status
    var progress: Double             // 0.0 - 1.0
    var retryCount: Int
    var createdAt: Date
    var updatedAt: Date
    var completedAt: Date?
    
    // 任务特定数据
    let inputData: [TaskName]Input
    var outputData: [TaskName]Output?
    
    // 错误信息
    var errorMessage: String?
    
    // MARK: - Initialization
    init(
        id: String = UUID().uuidString,
        inputData: [TaskName]Input
    ) {
        self.id = id
        self.status = .pending
        self.progress = 0.0
        self.retryCount = 0
        self.createdAt = Date()
        self.updatedAt = Date()
        self.inputData = inputData
    }
    
    // MARK: - Computed Properties
    var isActive: Bool {
        status == .pending || status == .processing
    }
    
    var canRetry: Bool {
        status == .failed && retryCount < [TaskName]Config.maxRetryCount
    }
}

// ============================================
// 输入/输出数据模型
// ============================================

struct [TaskName]Input: Codable {
    let sourceId: String
    let parameters: [String: String]
    // TODO: 添加具体输入字段
}

struct [TaskName]Output: Codable {
    let resultId: String
    let resultURL: String?
    // TODO: 添加具体输出字段
}

// ============================================
// 配置
// ============================================

enum [TaskName]Config {
    static let maxRetryCount = 3
    static let maxConcurrentTasks = 2
    static let pollingInterval: TimeInterval = 5.0      // 5秒
    static let exponentialBackoffBase: TimeInterval = 2.0
}
```

### 步骤 2: 创建任务持久化层

基于 JSON 文件的持久化实现：

```swift
import Foundation

/// [任务名]持久化仓库
actor [TaskName]Repository {
    // MARK: - Singleton
    static let shared = [TaskName]Repository()
    
    // MARK: - Properties
    private let fileManager = FileManager.default
    private let fileName = "[taskname]_jobs.json"
    
    private var fileURL: URL {
        let documentsPath = fileManager.urls(
            for: .documentDirectory,
            in: .userDomainMask
        ).first!
        return documentsPath.appendingPathComponent(fileName)
    }
    
    private init() {
        print("📦 [[TaskName]Repository] 初始化，文件路径: \(fileURL.path)")
    }
    
    // MARK: - CRUD Operations
    
    /// 保存单个任务
    func save(_ job: [TaskName]Job) async throws {
        var jobs = try await loadAll()
        
        // 更新或添加
        if let index = jobs.firstIndex(where: { $0.id == job.id }) {
            jobs[index] = job
        } else {
            jobs.append(job)
        }
        
        try await saveAll(jobs)
        print("💾 [[TaskName]Repository] 保存任务: \(job.id), 状态: \(job.status)")
    }
    
    /// 加载所有任务
    func loadAll() async throws -> [[TaskName]Job] {
        guard fileManager.fileExists(atPath: fileURL.path) else {
            print("📂 [[TaskName]Repository] 文件不存在，返回空数组")
            return []
        }
        
        let data = try Data(contentsOf: fileURL)
        let jobs = try JSONDecoder().decode([[TaskName]Job].self, from: data)
        print("📂 [[TaskName]Repository] 加载 \(jobs.count) 个任务")
        return jobs
    }
    
    /// 根据ID获取任务
    func load(id: String) async throws -> [TaskName]Job? {
        let jobs = try await loadAll()
        return jobs.first { $0.id == id }
    }
    
    /// 删除任务
    func delete(id: String) async throws {
        var jobs = try await loadAll()
        jobs.removeAll { $0.id == id }
        try await saveAll(jobs)
        print("🗑️ [[TaskName]Repository] 删除任务: \(id)")
    }
    
    /// 保存所有任务
    private func saveAll(_ jobs: [[TaskName]Job]) async throws {
        let data = try JSONEncoder().encode(jobs)
        try data.write(to: fileURL, options: .atomic)
    }
    
    /// 清理已完成任务（可选）
    func cleanup(olderThan days: Int = 7) async throws {
        let cutoffDate = Calendar.current.date(
            byAdding: .day,
            value: -days,
            to: Date()
        )!
        
        var jobs = try await loadAll()
        let beforeCount = jobs.count
        
        jobs.removeAll { job in
            guard job.status == .completed || job.status == .failed else {
                return false
            }
            return job.updatedAt < cutoffDate
        }
        
        try await saveAll(jobs)
        print("🧹 [[TaskName]Repository] 清理完成，删除 \(beforeCount - jobs.count) 个旧任务")
    }
}
```

### 步骤 3: 创建任务管理器

实现任务队列、轮询、重试等核心逻辑：

```swift
import Foundation
import Combine

/// [任务名]管理器
@MainActor
class [TaskName]Manager: ObservableObject {
    // MARK: - Singleton
    static let shared = [TaskName]Manager()
    
    // MARK: - Published Properties
    @Published private(set) var activeJobs: [[TaskName]Job] = []
    @Published private(set) var isProcessing = false
    
    // MARK: - Private Properties
    private let repository = [TaskName]Repository.shared
    private var pollingTasks: [String: Task<Void, Never>] = [:]
    private var cancellables = Set<AnyCancellable>()
    
    private init() {
        print("🚀 [[TaskName]Manager] 初始化")
        setupNotifications()
    }
    
    // MARK: - Public Methods
    
    /// 创建新任务
    func enqueue(inputData: [TaskName]Input) async -> [TaskName]Job {
        let job = [TaskName]Job(inputData: inputData)
        
        do {
            try await repository.save(job)
            await loadActiveJobs()
            await startPolling(for: job.id)
            
            print("✅ [[TaskName]Manager] 任务已入队: \(job.id)")
            
            // 发送通知
            NotificationCenter.default.post(
                name: .[TaskName]JobCreated,
                object: job
            )
            
            return job
        } catch {
            print("❌ [[TaskName]Manager] 任务入队失败: \(error)")
            return job
        }
    }
    
    /// 取消任务
    func cancel(jobId: String) async {
        guard var job = try? await repository.load(id: jobId) else {
            return
        }
        
        // 停止轮询
        pollingTasks[jobId]?.cancel()
        pollingTasks.removeValue(forKey: jobId)
        
        // 更新状态
        job.status = .cancelled
        job.updatedAt = Date()
        
        try? await repository.save(job)
        await loadActiveJobs()
        
        print("🚫 [[TaskName]Manager] 任务已取消: \(jobId)")
        
        // 发送通知
        NotificationCenter.default.post(
            name: .[TaskName]JobCancelled,
            object: job
        )
    }
    
    /// 恢复现有任务（app启动时调用）
    func rebindExistingTasks() async {
        print("🔄 [[TaskName]Manager] 恢复现有任务")
        
        await loadActiveJobs()
        
        for job in activeJobs where job.isActive {
            await startPolling(for: job.id)
        }
        
        print("✅ [[TaskName]Manager] 恢复了 \(activeJobs.count) 个活跃任务")
    }
    
    // MARK: - Private Methods
    
    /// 加载活跃任务
    private func loadActiveJobs() async {
        do {
            let allJobs = try await repository.loadAll()
            activeJobs = allJobs.filter { $0.isActive }
        } catch {
            print("❌ [[TaskName]Manager] 加载任务失败: \(error)")
        }
    }
    
    /// 开始轮询任务状态
    private func startPolling(for jobId: String) async {
        // 如果已在轮询，先取消
        pollingTasks[jobId]?.cancel()
        
        let pollingTask = Task {
            var delay: TimeInterval = [TaskName]Config.pollingInterval
            
            while !Task.isCancelled {
                do {
                    try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                    
                    guard let job = try await repository.load(id: jobId),
                          job.isActive else {
                        break
                    }
                    
                    // 调用后端API检查状态
                    let updatedJob = try await checkTaskStatus(job)
                    try await repository.save(updatedJob)
                    await loadActiveJobs()
                    
                    // 如果完成或失败，停止轮询
                    if updatedJob.status == .completed {
                        await handleJobCompleted(updatedJob)
                        break
                    } else if updatedJob.status == .failed {
                        await handleJobFailed(updatedJob)
                        break
                    }
                    
                    // 指数退避
                    delay = min(
                        delay * [TaskName]Config.exponentialBackoffBase,
                        60.0 // 最大60秒
                    )
                } catch {
                    print("⚠️ [[TaskName]Manager] 轮询出错: \(error)")
                    delay = min(delay * 1.5, 30.0)
                }
            }
            
            pollingTasks.removeValue(forKey: jobId)
        }
        
        pollingTasks[jobId] = pollingTask
    }
    
    /// 检查任务状态（调用后端API）
    private func checkTaskStatus(_ job: [TaskName]Job) async throws -> [TaskName]Job {
        // TODO: 实现后端API调用
        var updatedJob = job
        updatedJob.status = .processing
        updatedJob.progress = 0.5
        updatedJob.updatedAt = Date()
        return updatedJob
    }
    
    /// 处理任务完成
    private func handleJobCompleted(_ job: [TaskName]Job) async {
        print("✅ [[TaskName]Manager] 任务完成: \(job.id)")
        
        NotificationCenter.default.post(
            name: .[TaskName]JobCompleted,
            object: job
        )
    }
    
    /// 处理任务失败
    private func handleJobFailed(_ job: [TaskName]Job) async {
        print("❌ [[TaskName]Manager] 任务失败: \(job.id)")
        
        // 检查是否可以重试
        if job.canRetry {
            await retry(jobId: job.id)
        } else {
            NotificationCenter.default.post(
                name: .[TaskName]JobFailed,
                object: job
            )
        }
    }
    
    /// 重试失败的任务
    private func retry(jobId: String) async {
        guard var job = try? await repository.load(id: jobId) else {
            return
        }
        
        job.status = .pending
        job.retryCount += 1
        job.updatedAt = Date()
        
        try? await repository.save(job)
        await startPolling(for: jobId)
        
        print("🔄 [[TaskName]Manager] 重试任务: \(jobId), 第 \(job.retryCount) 次")
    }
    
    /// 设置生命周期通知
    private func setupNotifications() {
        // App进入后台
        NotificationCenter.default.publisher(for: UIApplication.didEnterBackgroundNotification)
            .sink { [weak self] _ in
                print("📱 [[TaskName]Manager] App进入后台")
            }
            .store(in: &cancellables)
        
        // App回到前台
        NotificationCenter.default.publisher(for: UIApplication.willEnterForegroundNotification)
            .sink { [weak self] _ in
                print("📱 [[TaskName]Manager] App回到前台")
                Task {
                    await self?.rebindExistingTasks()
                }
            }
            .store(in: &cancellables)
    }
}

// MARK: - Notification Names
extension Notification.Name {
    static let [TaskName]JobCreated = Notification.Name("[TaskName].jobCreated")
    static let [TaskName]JobCompleted = Notification.Name("[TaskName].jobCompleted")
    static let [TaskName]JobFailed = Notification.Name("[TaskName].jobFailed")
    static let [TaskName]JobCancelled = Notification.Name("[TaskName].jobCancelled")
}
```

### 步骤 4: 集成到 App 生命周期

在 `App.swift` 中初始化：

```swift
@main
struct PoseCamApp: App {
    init() {
        // 恢复后台任务
        Task {
            await [TaskName]Manager.shared.rebindExistingTasks()
        }
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

### 步骤 5: 在 ViewModel 中使用

```swift
class MyFeatureViewModel: ObservableObject {
    @Published var activeJob: [TaskName]Job?
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        setupNotifications()
    }
    
    func startTask(input: [TaskName]Input) {
        Task {
            let job = await [TaskName]Manager.shared.enqueue(inputData: input)
            await MainActor.run {
                self.activeJob = job
            }
        }
    }
    
    private func setupNotifications() {
        NotificationCenter.default.publisher(for: .[TaskName]JobCompleted)
            .sink { [weak self] notification in
                guard let job = notification.object as? [TaskName]Job else { return }
                self?.handleJobCompleted(job)
            }
            .store(in: &cancellables)
    }
    
    private func handleJobCompleted(_ job: [TaskName]Job) {
        print("任务完成: \(job.id)")
    }
}
```

## Best Practices

1. **持久化优先**: 任务状态实时保存到文件
2. **指数退避**: 轮询间隔动态调整
3. **重试机制**: 失败后自动重试，限制次数
4. **生命周期管理**: 支持app重启恢复
5. **通知机制**: 使用 NotificationCenter 解耦
6. **并发控制**: 限制同时执行的任务数

## Output Checklist

完成后确认：
- ✅ 任务数据模型已定义
- ✅ 持久化层已实现
- ✅ 任务管理器已创建
- ✅ 轮询和重试机制已配置
- ✅ App 生命周期集成完成
- ✅ 通知事件已定义
