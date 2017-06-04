'use strict';

function run_bench()
{
    var time_start = performance.now();
    var form = document.forms.bench_setting;
    Module._bench(form.mode.value, form.m.value, form.n.value, form.k.value, form.times.value);
    var time_end = performance.now();
    var iter_time = (time_end - time_start) / form.times.value;
    console.log('Time: ' + iter_time)
}
