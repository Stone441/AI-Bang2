"""Start a separate credential-free scenario lab on loopback, in memory only."""
import argparse
from brain.scenario_lab import ScenarioLab, create_lab_server


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=0)
    args=parser.parse_args();lab=ScenarioLab()
    server=create_lab_server(lab,args.port)
    print('SYNTHETIC SOURCES / FAKE EXTRACTIVE MODEL / ISOLATED OPERATOR LAB',flush=True)
    print(f'http://127.0.0.1:{server.server_port}/',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close();lab.close()


if __name__=='__main__':main()
