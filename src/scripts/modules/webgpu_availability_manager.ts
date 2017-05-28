// enum State {
//     SLEEP = 0,
//     RUNNING = 1,
//     DONE = 2
// }
//
// export default class AvailabilityManager {
//     private state: State = State.SLEEP;
//     private key: string;
//
//     constructor(key: string) {
//         this.key = key;
//     }
//
//     start() {
//
//     }
//
//     end() {
//
//     }
//
//     get availability() {
//         let savedState = parseInt(localStorage.getItem(this.key) || '0') as State;
//
//         switch (savedState) {
//             case State.SLEEP:
//                 return true;
//
//             case State.RUNNING:
//                 return this.state !== State.SLEEP;
//
//             case State.DONE:
//                 return true;
//         }
//
//     }