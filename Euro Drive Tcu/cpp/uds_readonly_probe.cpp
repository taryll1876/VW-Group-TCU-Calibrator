// Read-only UDS probe starter.
//
// This is a portable skeleton for teams that want a C++ implementation later.
// Platform-specific CAN/J2534 calls are intentionally left behind the
// sendCanFrame/receiveCanFrame placeholders.

#include <array>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>

struct CanFrame {
  std::uint32_t id;
  std::array<std::uint8_t, 8> data;
};

std::string hexBytes(const std::array<std::uint8_t, 8>& data) {
  std::ostringstream out;
  for (std::size_t i = 0; i < data.size(); ++i) {
    if (i != 0) {
      out << ' ';
    }
    out << std::uppercase << std::hex << std::setw(2) << std::setfill('0')
        << static_cast<int>(data[i]);
  }
  return out.str();
}

void sendCanFrame(const CanFrame& frame) {
  std::cout << "TX 0x" << std::hex << std::uppercase << frame.id << "  "
            << hexBytes(frame.data) << "\n";
}

std::optional<CanFrame> receiveCanFrame(std::uint32_t rxId) {
  return CanFrame{rxId, {0x02, 0x50, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00}};
}

int main() {
  constexpr std::uint32_t txId = 0x7E1;
  constexpr std::uint32_t rxId = 0x7E9;
  const CanFrame sessionRequest{txId, {0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00}};

  sendCanFrame(sessionRequest);
  const auto response = receiveCanFrame(rxId);
  if (!response.has_value()) {
    std::cerr << "No UDS response\n";
    return 1;
  }

  std::cout << "RX 0x" << std::hex << std::uppercase << response->id << "  "
            << hexBytes(response->data) << "\n";

  if (response->data[1] == 0x50 && response->data[2] == 0x03) {
    std::cout << "UDS handshake success\n";
    return 0;
  }

  std::cerr << "UDS handshake failed\n";
  return 2;
}
