// export enum Availability {
//     Maybe = 0,
//     Available = 1,
//     Unavaiable = 2
// }
//
// enum State {
//     SLEEP,
//     RUNNING,
//     DONE
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
//         let value = parseInt(localStorage.getItem(this.key) || '0') as Availability;
//
//         switch (value) {
//             case Availability.Maybe:
//                 return Availability.Maybe;
//             case Availability.Maybe:
//                 return Availability.Maybe;
//             case Availability.Maybe:
//                 return Availability.Maybe;
//         }
//
// }