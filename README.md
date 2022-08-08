# Distributed Routing in LEO Satellite Communication
We aim to pursue the problem as framed in III-E adapted
to our satellite topology. The distributed routing strategy as
shown in III-B shows great promise, and we plan to augment
it by making use of the distributed dynamic programming
algorithm which involves exchange of information between
nodes. As of now, the best approach seems to be leaving
the direction estimation and enhancement phases the same,
but modifying the congestion resolution phase. The main
idea behind modifying the congestion resolution phase is
that there are multiple paths in a dense mesh-like satellite
topology, but the spatial distribution of load across that mesh
may not be uniform. If the nodes could make better decisions
by knowing the traffic information at its neighbours, rather
than trying to guess that by estimating its own output buffers,
our claim is that the minimum delay would undoubtedly
improve. We could use the metrics defined in III-C to make
the decision, and tune the paramaters ($\alpha$, $\beta$, $\delta$, $\cdots$) to make
an optimized decision. We also plan to introduce some
stochastic behaviour based on the metrics, for example, if the
priority metric for a particular link is very high compared
to the others, then send the packet to that link with a very
high probability. At first glance, this looks like intentionally
degrading the performance of the algorithm, but we think
that it might alleviate deadlocks in congestion, and possibly
satellite failures.
## Routing according to logical locations
## Congestion control 