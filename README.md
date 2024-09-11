# better-codehs-karel 0.2.0
A simulator and library for the CodeHS Karel.

It has various benefits over the official CodeHS Karel, including but not limited to:

## Open-source / free software / libreware
The official CodeHS Karel is "all rights reserved", but better-codehs-karel is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

better-codehs-karel is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with better-codehs-karel. If not, see <https://www.gnu.org/licenses/>. 

## Infinite loops allowed & immediate output
The official CodeHS Karel crashes your browser if your program creates an infinite loop. This version allows infinite loops because it does not simulate until the end unless you let it go, allowing there to be no end but also allowing immediate output when you press the Run button.

## Easy to debug
The official CodeHS Karel makes it hard to debug, because it does not allow you to see the values of variables. The library stored inside this repository allows you to do so easily, because with it you can run an instance of a Karel world in a debugger, which has major advantages over just seeing what Karel does or even using `print` statements.
