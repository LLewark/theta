## What is this repository for?

This repository supplements the paper

> L. Lewark and C. Zibrowius, [_Rasmussen invariants of Whitehead doubles and other satellites_](https://arxiv.org/abs/2208.13612)

For any c equal to a prime number or 0, the paper defines certain knot invariants ϑ<sub>c</sub> that govern the behaviour of Rasmussen invariants over fields of characteristic c under satellite operations with patterns of winding number 0 and wrapping number 2.  

We collect all known ϑ<sub>c</sub>-invariants in the following table (`index.html`):

> [https://llewark.github.io/theta/](https://llewark.github.io/theta/).  

## What are the other files for?

The table is generated from the source file `data.csv` by running the script `converter.py`:

    ./converter.py data.csv > index.html

Each line of `data.csv` corresponds to one of the following: 

- a computation, in which case the format is a `tab` separated list of 
  - the knot id, e.g. `3_1` for the trefoil knot,
  - the invariant, e.g. `theta_2` for ϑ₂,
  - the value of the invariant, e.g. `4`,
  - metadata, which is formatted as a semi-colon (`;`) separated list of any number of 
    - colon (`:`) separated key-value pairs, e.g. `program:khoca` and
    - comments, e.g. `My computer was very tired after this computation.`
- a comment about a particular knot, in which case the format is a `tab` separated list of
  - the knot id and
  - a comment.

The script performs some basic sanity checks along the way. 
For example, it ensures that if multiple computations were made for the same invariant, the results all agree. 

## Where does the data come from?

The values for the ϑ<sub>c</sub>-invariants were computed using the following two programs:

- [khoca](http://lewark.de/lukas/khoca.html), a program for computing sl(N)-homology theories of knots, written by L. Lewark.  
  _Most computations were done using this program._
  
- [kht++](https://cbz20.raspberryip.com/code/khtpp/docs/index.html), a program for calculating the Khovanov and Bar-Natan homology of links and tangles, written by C. Zibrowius.  
  _Details for computations done with this program are available [here](https://cbz20.raspberryip.com/code/khtpp/examples/RasmussenSOfSatellites.html)._

The values of some other invariants, such as the τ invariant and the slice genus, were scraped from knotinfo:

> C. Livingston and A. H. Moore, [_KnotInfo_: Table of Knot Invariants](https://knotinfo.math.indiana.edu) 

For the source of any value, please check the metadata by clicking on the corresponding row of the table.
