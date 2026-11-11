#!/usr/bin/env bash
# 生成一个带故意缺陷的演示 Git 仓库，用于验证「代码评审 / 提测说明 / 回归清单」三个 skill。
# 所有代码、接口、密钥均为虚构数据，不包含任何公司真实信息。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ $# -gt 0 ]]; then
  DEST="$1"
else
  DEST="$(mktemp -d "${TMPDIR:-/tmp}/skill-contest-demo.XXXXXX")/DemoCarApp"
fi

if [[ -e "$DEST" ]]; then
  echo "错误：目标已存在，换一个路径或先手动确认删除：$DEST" >&2
  exit 1
fi

mkdir -p "$DEST"
cd "$DEST"
git init -q -b main
git config user.name "Demo Dev"
git config user.email "demo@example.com"
git config --local commit.gpgsign false

# ---------------------------------------------------------------- 初始版本
mkdir -p Sources/Common Sources/Network Sources/Vehicle Resources

cat > README.md <<'EOF'
# DemoCarApp

仅用于 Skill 演示的虚构车联网 App。所有接口、密钥、车辆数据均为假数据。
EOF

cat > Sources/AppDelegate.swift <<'EOF'
import UIKit

@main
final class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        Logger.info("App 启动")
        return true
    }
}
EOF

cat > Sources/Common/Logger.swift <<'EOF'
import Foundation

enum Logger {
    static func info(_ message: String) {
        #if DEBUG
        print("[INFO] \(message)")
        #endif
    }

    static func error(_ message: String, error: Error? = nil) {
        print("[ERROR] \(message) \(error?.localizedDescription ?? "")")
    }
}
EOF

cat > Sources/Network/APIClient.swift <<'EOF'
import Foundation

final class APIClient {
    static let shared = APIClient()
    private let session = URLSession.shared

    func request<T: Decodable>(_ urlString: String, completion: @escaping (Result<T, Error>) -> Void) {
        guard let url = URL(string: urlString) else {
            completion(.failure(NSError(domain: "APIClient", code: -1,
                                        userInfo: [NSLocalizedDescriptionKey: "无效的 URL"])))
            return
        }

        session.dataTask(with: url) { data, _, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            guard let data = data else {
                completion(.failure(NSError(domain: "APIClient", code: -2,
                                            userInfo: [NSLocalizedDescriptionKey: "空响应"])))
                return
            }
            do {
                let value = try JSONDecoder().decode(T.self, from: data)
                completion(.success(value))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}
EOF

cat > Sources/Vehicle/VehicleService.swift <<'EOF'
import Foundation

struct Vehicle: Codable {
    let id: String
    let name: String
    let plateNumber: String
}

final class VehicleService {
    func fetchVehicles(completion: @escaping (Result<[Vehicle], Error>) -> Void) {
        APIClient.shared.request("https://api.example.com/v1/vehicles", completion: completion)
    }
}
EOF

cat > Sources/Vehicle/VehicleListViewController.swift <<'EOF'
import UIKit

final class VehicleListViewController: UIViewController {
    private let tableView = UITableView()
    private var vehicles: [Vehicle] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "我的车辆"
        tableView.dataSource = self
        view.addSubview(tableView)
        loadVehicles()
    }

    private func loadVehicles() {
        VehicleService().fetchVehicles { [weak self] result in
            switch result {
            case .success(let list):
                DispatchQueue.main.async {
                    self?.vehicles = list
                    self?.tableView.reloadData()
                }
            case .failure(let error):
                Logger.error("车辆列表加载失败", error: error)
            }
        }
    }
}

extension VehicleListViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        vehicles.count
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "VehicleCell", for: indexPath)
        cell.textLabel?.text = vehicles[indexPath.row].name
        return cell
    }
}
EOF

cat > Resources/Localizable.strings <<'EOF'
"vehicle_list_title" = "我的车辆";
EOF

cat > .regression-map.yml <<'EOF'
project: DemoCarApp
modules:
  - name: 车辆列表
    paths:
      - "Sources/Vehicle/VehicleListViewController.swift"
    priority: P0
    test_steps:
      - 打开 App，进入「我的车辆」
      - 检查列表加载、下拉刷新、空列表展示
  - name: 远程空调
    paths:
      - "Sources/Vehicle/RemoteClimateService.swift"
    priority: P0
    test_steps:
      - 选择一辆车，点击「远程开空调」
      - 检查温度参数、成功提示、失败提示
  - name: 车门控制
    paths:
      - "Sources/Vehicle/DoorService.swift"
    priority: P0
    test_steps:
      - 点击「解锁车门」，检查成功与失败提示
      - 检查登录态失效时的表现
  - name: 网络层
    paths:
      - "Sources/Network/APIClient.swift"
    priority: P1
    test_steps:
      - 断开网络后重试
      - 模拟接口返回非法 JSON
      - 模拟接口超时
  - name: 多语言
    paths:
      - "Resources/Localizable.strings"
    priority: P2
    test_steps:
      - 切换语言后检查文案
      - 检查长文案是否截断
EOF

git add -A
git commit -q -m "chore: 初始化 DemoCarApp 工程"
git tag v1.1.0

# ------------------------------------------------------------ 功能分支
git checkout -q -b feature/remote-control

cat > Sources/Vehicle/RemoteClimateService.swift <<'EOF'
import Foundation

struct ClimateState: Codable {
    let isOn: Bool
    let temperature: Int
}

final class RemoteClimateService {
    static let shared = RemoteClimateService()

    private var pendingCommands: [String] = []
    private var onStateChanged: ((Bool) -> Void)?

    func observeState(_ handler: @escaping (Bool) -> Void) {
        onStateChanged = handler
    }

    func startClimate(vehicleId: String, temperature: Int) {
        pendingCommands.append(vehicleId)

        let url = "https://api.example.com/v1/vehicles/\(vehicleId)/climate?temperature=\(temperature)"
        APIClient.shared.request(url) { (result: Result<ClimateState, Error>) in
            switch result {
            case .success(let state):
                self.onStateChanged?(state.isOn)
            case .failure(let error):
                Logger.error("远程空调启动失败", error: error)
            }
        }
    }

    func cancelAllPending() {
        pendingCommands.removeAll()
    }
}
EOF

cat > Sources/Vehicle/VehicleListViewController.swift <<'EOF'
import UIKit

final class VehicleListViewController: UIViewController {
    private let tableView = UITableView()
    private let climateButton = UIButton(type: .system)
    private var vehicles: [Vehicle] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "我的车辆"
        tableView.dataSource = self
        view.addSubview(tableView)
        view.addSubview(climateButton)

        climateButton.setTitle("远程开空调", for: .normal)
        climateButton.addTarget(self, action: #selector(openFirstVehicle), for: .touchUpInside)

        observeClimate()
        loadVehicles()
    }

    private func loadVehicles() {
        VehicleService().fetchVehicles { [weak self] result in
            switch result {
            case .success(let list):
                self?.vehicles = list
                self?.tableView.reloadData()
            case .failure(let error):
                Logger.error("车辆列表加载失败", error: error)
            }
        }
    }

    private func observeClimate() {
        RemoteClimateService.shared.observeState { isOn in
            self.tableView.reloadData()
        }
    }

    @objc private func openFirstVehicle() {
        let vehicle = vehicles[0]
        RemoteClimateService.shared.startClimate(vehicleId: vehicle.id, temperature: 24)
    }
}

extension VehicleListViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        vehicles.count
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "VehicleCell", for: indexPath)
        cell.textLabel?.text = vehicles[indexPath.row].name
        return cell
    }
}
EOF

git add -A
git commit -q -m "feat: 新增远程空调控制"

# ------------------------------------------------------------ 车门控制
cat > Sources/Vehicle/DoorService.swift <<'EOF'
import Foundation

final class DoorService {
    // FIXME: 临时写死，联调后替换
    private let apiToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vIn0.fake-signature"

    func unlock(vehicleId: String, completion: @escaping (Bool) -> Void) {
        let urlString = "https://api.example.com/v1/vehicles/\(vehicleId)/door/unlock"
        var request = URLRequest(url: URL(string: urlString)!)
        request.httpMethod = "POST"
        request.setValue("Bearer \(apiToken)", forHTTPHeaderField: "Authorization")

        URLSession.shared.dataTask(with: request) { _, response, error in
            if let error = error {
                Logger.error("解锁失败", error: error)
                completion(false)
                return
            }
            let http = response as! HTTPURLResponse
            completion(http.statusCode == 200)
        }.resume()
    }
}
EOF

git add -A
git commit -q -m "fix: 修复车门解锁失败无提示"

# ------------------------------------------------------------ 网络层重构
cat > Sources/Network/APIClient.swift <<'EOF'
import Foundation

final class APIClient {
    static let shared = APIClient()
    private let session = URLSession.shared
    private var pollingTimer: Timer?

    func request<T: Decodable>(_ urlString: String, completion: @escaping (Result<T, Error>) -> Void) {
        guard let url = URL(string: urlString) else { return }

        session.dataTask(with: url) { data, _, _ in
            guard let data = data else { return }
            let value = try? JSONDecoder().decode(T.self, from: data)
            if let value = value {
                completion(.success(value))
            }
        }.resume()
    }

    func startTokenPolling() {
        pollingTimer = Timer.scheduledTimer(withTimeInterval: 60, repeats: true) { _ in
            self.refreshToken()
        }
    }

    private func refreshToken() {
        Logger.info("刷新 token")
    }
}
EOF

git add -A
git commit -q -m "refactor: 统一网络层错误处理"

# ------------------------------------------------------------ 多语言
cat > Resources/Localizable.strings <<'EOF'
"vehicle_list_title" = "我的车辆";
"vehicle_climate_open" = "远程开空调";
"vehicle_climate_running" = "空调运行中";
"vehicle_door_unlock" = "解锁车门";
"vehicle_door_failed" = "解锁失败，请重试";
EOF

git add -A
git commit -q -m "chore: 补充远程控制相关文案"

echo "✅ 演示仓库已生成: $DEST"
echo
echo "分支: main（初始版本，tag v1.1.0） / feature/remote-control（4 次提交，含故意缺陷）"
echo "回归映射: $DEST/.regression-map.yml"
echo
echo "下一步可以运行:"
if [[ -f "$SKILL_DIR/scripts/collect_diff.sh" ]]; then
  echo "  bash \"$SKILL_DIR/scripts/collect_diff.sh\" --repo \"$DEST\" --base main --target feature/remote-control --out /tmp/demo-diff.txt"
elif [[ -f "$SKILL_DIR/scripts/collect_changes.sh" ]]; then
  echo "  bash \"$SKILL_DIR/scripts/collect_changes.sh\" --repo \"$DEST\" --base main --target feature/remote-control --out /tmp/demo-changes.txt"
else
  echo "  python3 \"$SKILL_DIR/scripts/generate_checklist.py\" --repo \"$DEST\" --base main --target feature/remote-control --map .regression-map.yml --format xlsx --out /tmp/regression.xlsx"
fi
