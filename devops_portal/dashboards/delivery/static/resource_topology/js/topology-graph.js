
var ResourceTopologyGraph = function(dataUrl, graphSelector) {
    var content_width = $(graphSelector).innerWidth(),
        graph = this,
        w = content_width,
        h = content_width,
        rx = w / 2,
        ry = h / 2,
        m0, rotate = 0,
        pi = Math.PI,
        precis_text, active_link, color = d3.scale.ordinal().domain([-3, -2, -1, 0, 1, 2, 3]).range(["#2C2B1A", "#2C2B1A", "#2C2B1A", "#2C2B1A", "#2C2B1A", "#2C2B1A", "#2C2B1A"]),
        color_arc = d3.scale.ordinal().domain([-3, -2, -1, 0, 1, 2, 3]).range(["#FDB613", "#FDB613", "#2C2B1A", "#FDB613", "#FDB613", "#FDB613", "#FDB613"]),
        //var color_link = d3.scale.linear().domain([1, 3, 5]).range(["#C7C7C7", "#000000", "#000000"]);
        color_link = d3.scale.linear().domain([1, 6]).range(["#C7C7C7", "#000000"]),
        splines = [],
        cross = function(a, b) {
            return a[0] * b[1] - a[1] * b[0];
        },
        dot = function(a, b) {
            return a[0] * b[0] + a[1] * b[1];
        },
        mouseCoordinates = function(e) {
            return [e.pageX - rx, e.pageY - ry];
        };
    var nodeHelpers = {
      // Lazily construct the package hierarchy from class names.
      root: function(classes) {
        var map = {};
        function find(name, data) {
          var node = map[name], i;
          if (!node) {
            node = map[name] = data || {name: name, children: []};
            if (name.length) {
              node.parent = find(name.substring(0, i = name.lastIndexOf("|")));
              node.parent.children.push(node);
              node.key = name.substring(i + 1);
            }
          }
          return node;
        }

        classes.forEach(function(d) {
          find(d.name, d);
        });

        return map[""];
      },

      // Return a list of imports for the given array of nodes.
      imports: function(nodes) {
        var map = {},
            imports = [];

        // Compute a map from name to node.
        nodes.forEach(function(d) {
          map[d.name] = d;
        });

        // For each import, construct a link from the source to target node.
        nodes.forEach(function(d) {
          if (d.imports) {
            d.imports.forEach(function(i) {
                 j_found=0;
                 for (j=0; j<map[d.name].imports.length; j++)
                    if (map[d.name].imports[j].split("|").pop().match(map[i].key))
                        j_found = j;

                imports.push({source: map[d.name], target: map[i], link_str: d.lnkstrength[j_found]});
            });
          }
        });
        return imports;
      }
    };
    this.init = function() {
        graph.cluster = d3.layout.cluster()
            .size([360, ry - 150])
            .sort(function(a, b) {
                return d3.ascending(a.key, b.key);
            });
        graph.bundle = d3.layout.bundle();
        graph.line = d3.svg.line.radial()
            .interpolate("bundle")
            .tension(.8)
            .radius(function(d) {
                return d.y - 35;
            })
            .angle(function(d) {
                return d.x / 180 * pi;
            });
        // Chrome 15 bug: <http://code.google.com/p/chromium/issues/detail?id=98951>
        graph.div = d3.select(graphSelector).insert("div", "h2")
            .style("width", w + "px")
            .style("height", w + "px")
            .style("position", "absolute");
        graph.svg = graph.div.append("svg:svg")
            .attr("width", w)
            .attr("height", h)
            .append("svg:g")
            .attr("transform", "translate(" + rx + "," + ry + ")")
            .attr("transform", "rotate(180 " + rx / 2 + " " + ry / 2 + ")")

        graph.svg.append("svg:path")
            .attr("class", "arc")
            .attr("d", d3.svg.arc().outerRadius(ry - 120).innerRadius(0).startAngle(0).endAngle(2 * Math.PI))

        //d3.json("/static/dashboard/js/new-structure-sample.js", function(classes) {
        d3.json(dataUrl, this.render);

        d3.select(window).on("mousemove", function() {
            if (m0) {
                var m1 = mouseCoordinates(d3.event),
                    dm = Math.atan2(cross(m0, m1), dot(m0, m1)) * 180 / Math.PI;
                graph.div.style("-webkit-transform", "translate3d(0," + (ry - rx) + "px,0)rotate3d(0,0,0," + dm + "deg)translate3d(0," + (rx - ry) + "px,0)");
            }
        });
    };
    this.render = function(classes) {
        var nodes = graph.cluster.nodes(nodeHelpers.root(classes)),
            links = nodeHelpers.imports(nodes),
            splines = graph.bundle(links);

        var groupData = graph.svg.selectAll("g.group")
            .data(nodes.filter(function(d) {
                return (d.key == d.name.split("|")[0]) && d.children;
            }))
            .enter().append("group")
            .attr("class", "group");

        var groupArc = d3.svg.arc()
            .innerRadius(ry - 185)
            .outerRadius(ry - 160)
            .startAngle(function(d) {
                return (graph.findStartAngle(d.__data__.children) - 3) * pi / 180;
            })
            .endAngle(function(d) {
                return (graph.findEndAngle(d.__data__.children) + 3) * pi / 180
            });

        graph.svg.selectAll("g.arc")
            .data(groupData[0])
            .enter().append("svg:path")
            .attr("d", groupArc)
            .attr("class", "groupArc")
            .style("fill", function(d) {
                return color_arc(d.__data__.children);
            })
            .style("fill-opacity", 0.9);

        graph.svg.selectAll("g.node")
            .data(nodes.filter(function(n) {
                return !n.children;
            }))
            .enter().append("svg:g")
            .attr("class", "node")
            .attr("id", function(d) {
                return "node-" + d.key;
            })
            .attr("transform", function(d) {
                return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")";
            })
            .append("svg:a")

            .append("svg:text")
            .attr("dx", function(d) {
                return d.x < 180 ? 0 : 0;
            })
            .attr("dy", ".2em")
            .attr("text-anchor", function(d) {
                return d.x < 180 ? "start" : "end";
            })
            .style("fill", function(d) {
                return color(d.name.split("|")[0]);
            })
            .style("text-anchor", function(d) {
                return d.x < 180 ? "end" : "start";
            })
            .attr("transform", function(d) {
                return d.x < 180 ? "rotate(180)" : "rotate(0)";
            })
            .text(function(d) {
                return d.name.replace("_", " ").replace("_", " ");
            })
            .on("mouseover", function(d) {
                graph.svg.selectAll("path.link.target-" + d.key)
                    .classed("target", true)
                    .style("stroke", "red")
                    .each(graph.updateNodes("source", true));

                graph.svg.selectAll("path.link.source-" + d.key)
                    .classed("source", true)
                    .style("stroke", "red")
                    .each(graph.updateNodes("target", true));

                var k = d.name.split("|").pop();

                graph.svg.select("#node-" + d.key).classed("selected", true);
            })
            .on("mouseout", function mouseout(d) {
                graph.svg.selectAll("path.link.source-" + d.key)
                    .classed("source", false)
                    .each(graph.updateNodes("target", false))
                    .style("stroke", function(d) {
                        return color_link(d.link_str);
                    });

                graph.svg.selectAll("path.link.target-" + d.key)
                    .classed("target", false)
                    .each(graph.updateNodes("source", false))
                    .style("stroke", function(d) {
                        return color_link(d.link_str);
                    });

                graph.svg.select("#node-" + d.key).classed("selected", false);
            });

        var path = graph.svg.selectAll("path.link")
            .data(links)
            .enter().append("svg:a")
            .append("svg:path")
            .attr("class", function(d) {
                return "link source-" + d.source.key + " target-" + d.target.key;
            })
            .attr("d", function(d, i) {
                return line(splines[i]);
            })
            .style("stroke", function(d) {
                return color_link(d.link_str);
            })
            .on("mouseover", function linkMouseover(d) {
                active_link = ".source-" + d.source.key + ".target-" + d.target.key;
                graph.svg.selectAll(active_link).classed("active", true)
                    .style("stroke", "red");

                graph.svg.select("#node-" + d.source.key)
                    .classed("source", true);

                graph.svg.select("#node-" + d.target.key)
                    .classed("target", true);

                var s = d.source.key,
                    t = d.target.key;
                //TODO: wtf?
            })
            .on("mouseout", function linkMouseout(d) {
                graph.svg.selectAll(active_link).classed("active", false)
                    .style("stroke", function(d) {
                        return color_link(d.link_str);
                    });

                graph.svg.select("#node-" + d.source.key)
                    .classed("source", false);

                graph.svg.select("#node-" + d.target.key)
                    .classed("target", false);
            });

        var formatNumber = d3.format(',d');
        var nlength = formatNumber(nodes.length) - 7;
    };

    this.updateNodes = function(name, value) {
        return function(d) {
            if (value) this.parentNode.appendChild(this);
            graph.svg.select("#node-" + d[name].key).classed(name, value);
        };
    };

    this.findStartAngle = function(children) {
        var min = children[0].x;
        children.forEach(function(d) {
            if (d.x < min)
                min = d.x;
        });
        return min;
    };

    this.findEndAngle = function(children) {
        var max = children[0].x;
        children.forEach(function(d) {
            if (d.x > max)
                max = d.x;
        });
        return max;
    };
};