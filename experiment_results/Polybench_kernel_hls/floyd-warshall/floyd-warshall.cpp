#include "floyd-warshall.h"

#include "ap_fixed.h"
#include "hls_math.h"

void kernel_floyd_warshall(
			   int path[ 60 + 0][60 + 0])
{
  #pragma HLS top name=kernel_floyd_warshall

    const int n = 60;

  int i, j, k;

L1:  for (k = 0; k < n; k++)
    {
L2:      for(i = 0; i < n; i++)
L3:	for (j = 0; j < n; j++)
	  path[i][j] = path[i][j] < path[i][k] + path[k][j] ?
	    path[i][j] : path[i][k] + path[k][j];
    }

}