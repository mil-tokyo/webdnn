namespace WebDNN {
    export namespace Math {
        /**
         * Return indices of the top-K largest samples.
         * @param arr array
         * @param k number of indices
         * @returns {number[]} indices of top-K largest samples
         */
        export function argmax(arr: number[], k: number = 1) {
            arr = arr.slice();
            let stack = [[0, arr.length]];
            let workspace: { [key: number]: number } = {};

            while (stack.length > 0) {
                let fromTo = stack.shift()!, from = fromTo[0], to = fromTo[1],
                    pivot = arr[to - 1],
                    left = from,
                    right = to - 2,
                    tmp;

                if (from >= to) continue;

                while (true) {
                    while (arr[left] > pivot && left <= right) left++;
                    while (arr[right] <= pivot && left <= right) right--;

                    if (left >= right) break;
                    tmp = arr[left] || left;
                    arr[left] = arr[right] || right;
                    arr[right] = tmp;

                    tmp = workspace[left] || left;
                    workspace[left] = workspace[right] || right;
                    workspace[right] = tmp;
                }

                if (left != to - 1) {
                    arr[to - 1] = arr[left];
                    arr[left] = pivot;

                    tmp = workspace[to - 1] || to - 1;
                    workspace[to - 1] = workspace[left] || left;
                    workspace[left] = tmp;
                }

                stack.unshift([from, left]);
                if (left + 1 < k) stack.unshift([left + 1, to]);
            }

            let result: number[] = [];
            for (let i = 0; i < k; i++) {
                result.push(i in workspace ? workspace[i] : i);
            }

            return result;
        }

        /**
         * Return indices of the top-K smallest samples.
         * @param arr array
         * @param k number of indices
         * @returns {number[]} indices of top-K smallest samples
         */
        export function argmin(arr: number[], k: number = 1) {
            arr = arr.slice();
            let stack = [[0, arr.length]];
            let workspace: { [key: number]: number } = {};

            while (stack.length > 0) {
                let fromTo = stack.shift()!, from = fromTo[0], to = fromTo[1],
                    pivot = arr[to - 1],
                    left = from,
                    right = to - 2,
                    tmp;

                if (from >= to) continue;

                while (true) {
                    while (arr[left] < pivot && left <= right) left++;
                    while (arr[right] >= pivot && left <= right) right--;

                    if (left >= right) break;
                    tmp = arr[left] || left;
                    arr[left] = arr[right] || right;
                    arr[right] = tmp;

                    tmp = workspace[left] || left;
                    workspace[left] = workspace[right] || right;
                    workspace[right] = tmp;
                }

                if (left != to - 1) {
                    arr[to - 1] = arr[left];
                    arr[left] = pivot;

                    tmp = workspace[to - 1] || to - 1;
                    workspace[to - 1] = workspace[left] || left;
                    workspace[left] = tmp;
                }

                stack.unshift([from, left]);
                if (left + 1 < k) stack.unshift([left + 1, to]);
            }

            let result: number[] = [];
            for (let i = 0; i < k; i++) {
                result.push(i in workspace ? workspace[i] : i);
            }

            return result;
        }
    }
}
