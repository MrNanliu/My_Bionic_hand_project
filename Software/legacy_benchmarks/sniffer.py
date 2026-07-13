import socket
import serial
import argparse

def test_udp(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    sock.settimeout(5.0)
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            print(f"UDP [{addr}]: {data}")
        except socket.timeout:
            print("UDP timeout")
            break
        except KeyboardInterrupt:
            break

def test_serial(com_port, baud_rate):
    try:
        ser = serial.Serial(com_port, baud_rate, timeout=1)
        while True:
            if ser.in_waiting:
                data = ser.readline()
                print(f"Serial: {data}")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['udp', 'serial'], required=True)
    parser.add_argument('--ip', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--com', type=str, default='COM1')
    parser.add_argument('--baud', type=int, default=115200)
    args = parser.parse_args()

    if args.mode == 'udp':
        test_udp(args.ip, args.port)
    elif args.mode == 'serial':
        test_serial(args.com, args.baud)