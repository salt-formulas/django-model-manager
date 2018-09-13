var ResourceTopologyGraphs = function(ResourceTopologyGraphs){
    /**
     * Linear topology graph render method
     * @param dataUrl - URL to data endpoint
     * @param graphSelector - CSS selector of graph parent div
     * @param refreshInterval - Refresh interval in seconds (can be null, means refresh disabled)
     */
    ResourceTopologyGraphs.linear = function(dataUrl, graphSelector, refreshInterval){
      var marginLeft = 125,
          height = 2400,
          positioningMagicNumber = 20,
          content_width = $(graphSelector).innerWidth(),
          width = content_width,
          graph = this;

      this._data={};
      this.init = function(reinit){
          graph.cluster = d3.layout.cluster()
              .size([height, width])
              .sort(function(a, b) { return d3.ascending(a.name, b.name); })
              .value(function(d) { return d.service.length; });

          graph.bundle = d3.layout.bundle();

          graph.line = d3.svg.line()
              .interpolate("bundle")
              .tension(.85)
              .x(function(d) { return d.y; })
              .y(function(d) { return d.x; });
          if(reinit && graph.svg){
             d3.selectAll(graphSelector + " svg").remove();
          }
          graph.svg = d3.select(graphSelector).append("svg")
              .attr("width", width - positioningMagicNumber)
              .attr("height", height)
            .append("g")
              .attr("transform", "translate(-" + marginLeft + ", 0)");

          if(!reinit){
            graph.requestData(dataUrl, graph.render);
            $(window).on('resize', function(ev){
                graph.resetPosition();
                graph.init(true);
                graph.render();
            });

            if(refreshInterval){
                setInterval(function(){
                    graph.requestData(dataUrl, function(){
                        graph.init(true);
                        graph.render();
                    });
                }, refreshInterval * 1000);
            }
        }
      };
      this.render = function(){
        var nodes = graph.cluster.nodes(graphHelpers.root(graph._data)),
            links = graphHelpers.imports(nodes);

        graph.svg.selectAll(".link")
            .data(graph.bundle(links))
          .enter().append("path")
            .attr("class", "link")
            .attr("d", graph.line);

        graph.svg.selectAll(".node")
            .data(nodes.filter(function(n) { return !n.children; }))
          .enter().append("g")
            .attr("class", "node")
            .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
            .attr("data-host-id", function(d){ return d.host; })
          .append("text")
            .attr("dx", 8)
            .attr("dy", ".31em")
            .text(function(d) { return d.service; });

          d3.select(self.frameElement).style("height", height + "px");
      };

      this.requestData = function(dataUrl, callback){
            d3.json(dataUrl, function(res){
                if(res && res.result === 'ok'){
                    graph._data = res.data;
                    if(typeof callback === 'function'){
                        callback();
                    }
                }else{
                    console.log("Cannot create topology graph, server returns error: " + res.data);
                }
            });
        };
        this.resetPosition = function(){
            var sidebarWidth = $("#sidebar").width(),
                windowWidth = $(window).width();
            if(windowWidth > sidebarWidth){
                content_width = windowWidth - sidebarWidth + positioningMagicNumber;
            }else{
                content_width = windowWidth;
            }
            width = content_width - marginLeft;
        };
    };
    return ResourceTopologyGraphs;
}(ResourceTopologyGraphs || {});