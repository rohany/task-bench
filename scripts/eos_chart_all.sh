#!/bin/bash


./render_metg.py ../flops_stencil1d_eos_gpu_1node.csv \
           --xlabel 'Problem Size' \
           --xdata 'iterations' \
           --x-invert \
           --no-xticks \
           --ylabel 'TFLOP/s' \
           --yscale 1e-12 \
           --no-ylog \
           --highlight-column 'metg'
./render_metg.py ../flops_stencil1d_4g_eos_gpu_1node.csv \
           --xlabel 'Problem Size' \
           --xdata 'iterations' \
           --x-invert \
           --no-xticks \
           --ylabel 'TFLOP/s' \
           --yscale 1e-12 \
           --no-ylog \
           --highlight-column 'metg'
./render_metg.py ../efficiency_stencil1d_eos_gpu_1node.csv \
               --legend-position 'lower left' \
               --xlabel 'Task Granularity (ms)' \
               --xdata 'time_per_task' \
               --x-invert \
               --xbase 10 \
               --no-xticks \
               --ylabel 'Efficiency' \
               --ylim '(-0.05,1.05)' \
               --no-ylog \
               --y-percent \
               --highlight-column 'metg'
./render_metg.py ../efficiency_stencil1d_4g_eos_gpu_1node.csv \
               --legend-position 'lower left' \
               --xlabel 'Task Granularity (ms)' \
               --xdata 'time_per_task' \
               --x-invert \
               --xbase 10 \
               --no-xticks \
               --ylabel 'Efficiency' \
               --ylim '(-0.05,1.05)' \
               --no-ylog \
               --y-percent \
               --highlight-column 'metg'

./render_metg.py ../flops_stencil1d_eos_gpu_2node.csv \
           --xlabel 'Problem Size' \
           --xdata 'iterations' \
           --x-invert \
           --no-xticks \
           --ylabel 'TFLOP/s' \
           --yscale 1e-12 \
           --no-ylog \
           --highlight-column 'metg'
./render_metg.py ../flops_stencil1d_4g_eos_gpu_2node.csv \
           --xlabel 'Problem Size' \
           --xdata 'iterations' \
           --x-invert \
           --no-xticks \
           --ylabel 'TFLOP/s' \
           --yscale 1e-12 \
           --no-ylog \
           --highlight-column 'metg'
./render_metg.py ../efficiency_stencil1d_eos_gpu_2node.csv \
               --legend-position 'lower left' \
               --xlabel 'Task Granularity (ms)' \
               --xdata 'time_per_task' \
               --x-invert \
               --xbase 10 \
               --no-xticks \
               --ylabel 'Efficiency' \
               --ylim '(-0.05,1.05)' \
               --no-ylog \
               --y-percent \
               --highlight-column 'metg'
./render_metg.py ../efficiency_stencil1d_4g_eos_gpu_2node.csv \
               --legend-position 'lower left' \
               --xlabel 'Task Granularity (ms)' \
               --xdata 'time_per_task' \
               --x-invert \
               --xbase 10 \
               --no-xticks \
               --ylabel 'Efficiency' \
               --ylim '(-0.05,1.05)' \
               --no-ylog \
               --y-percent \
               --highlight-column 'metg'

./render_metg.py ../flops_stencil1d_eos_gpu_4node.csv \
           --xlabel 'Problem Size' \
           --xdata 'iterations' \
           --x-invert \
           --no-xticks \
           --ylabel 'TFLOP/s' \
           --yscale 1e-12 \
           --no-ylog \
           --highlight-column 'metg'
./render_metg.py ../flops_stencil1d_4g_eos_gpu_4node.csv \
           --xlabel 'Problem Size' \
           --xdata 'iterations' \
           --x-invert \
           --no-xticks \
           --ylabel 'TFLOP/s' \
           --yscale 1e-12 \
           --no-ylog \
           --highlight-column 'metg'
./render_metg.py ../efficiency_stencil1d_eos_gpu_4node.csv \
               --legend-position 'lower left' \
               --xlabel 'Task Granularity (ms)' \
               --xdata 'time_per_task' \
               --x-invert \
               --xbase 10 \
               --no-xticks \
               --ylabel 'Efficiency' \
               --ylim '(-0.05,1.05)' \
               --no-ylog \
               --y-percent \
               --highlight-column 'metg'
./render_metg.py ../efficiency_stencil1d_4g_eos_gpu_4node.csv \
               --legend-position 'lower left' \
               --xlabel 'Task Granularity (ms)' \
               --xdata 'time_per_task' \
               --x-invert \
               --xbase 10 \
               --no-xticks \
               --ylabel 'Efficiency' \
               --ylim '(-0.05,1.05)' \
               --no-ylog \
               --y-percent \
               --highlight-column 'metg'
