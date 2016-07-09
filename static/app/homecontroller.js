/**
 * Created by Hope on 6/18/2016.
 */
'use strict';   // See note about 'use strict'; below

var myApp = angular.module('myApp', []);

myApp.controller('MyCtrl', MyCtrl)
    .directive("graphDirective", function () {
        return {
            template: ""
        };
    })
    .factory("jsService", function () {
        // here goes the code of your js (d3 in my case)
        //now return the object of the service

        return d3;
    });

function MyCtrl($scope, $http, $window) {


    $scope.some_data =
    {
        "nodes": [],
        "edges": []
    };
    $scope.config = {
        dataSource: $scope.some_data
    };

    $scope.alchemy = new $window.Alchemy($scope.config);

    $scope.explorebool = false;
    $scope.exploretext = "View Graph";
    $scope.explorecurrent = "Messages";
    $scope.currentEntities = [
        {img: "None", name: "channel1"}
    ];
    $scope.typeOptions = [
        {name: 'Explore by Topic', value: 'feature'}
        // {name: 'Explore by Intent', value: 'bug'},
        // {name: 'Explore by Type', value: 'enhancement'}
    ];
    $scope.channels = [
        {name: 'Channel 1', value: 'feature'},
        {name: 'Channel 1', value: 'feature'},
        {name: 'Channel 1', value: 'feature'},
        {name: 'Channel 1', value: 'feature'}
    ];
    $scope.form = {type: $scope.typeOptions[0].value};
    $scope.responseobject = "RESPONSE OBJECT GOES HERE";
    $scope.graphstyle = "background-color:rgba(0, 0, 0, 0.5) !important;";

    $scope.switchExplore = function () {
        $scope.explorebool = !$scope.explorebool;
        $scope.exploretext = $scope.explorebool ? "View Graph" : "View Messages";
        $scope.explorecurrent = !$scope.explorebool ? "Graph" : "Messages";

    };
    $scope.switchCatSelection = function (entity) {
        $scope.selectedCatItem = entity.name;
        $scope.getGraphData(entity.id);
        console.log(entity);

    };

    $scope.testAPI = function () {
        $http({
            method: 'GET',
            url: '/api/getchannels'
        }).then(function successCallback(response) {
            $scope.responseobject = response.data;
            $scope.channels = [];
            // $scope.channels.push({img: "None", name: "All Channels"});
            response.data.channels.forEach(function (channelobj) {
                $scope.channels.push({img: "None", name: channelobj.name});
            });
        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response)
        });
    };
    $scope.getUsers = function () {
        $http({
            method: 'GET',
            url: '/api/getcategories'
        }).then(function successCallback(response) {
            $scope.responseobject = response.data;
            $scope.currentEntities = [];
            // console.log(response);
            // $scope.channels.push({img: "None", name: "All Channels"});
            response.data.members.forEach(function (member) {
                $scope.currentEntities.push({img: "None", name: member.name, id: member.id});

            });
            // console.log($scope.channels, "we made it")
        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response)
        });
    };
    $scope.getGraphData = function (entityid) {
        $http({
            url: '/api/getexploredata',
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(entityid)
        }).success(function (data) {

            // $scope.alchemy.Remove();
            var nodes = $scope.alchemy.get.allNodes("all");
            var edges = $scope.alchemy.get.allEdges();

            $scope.alchemy.remove.nodes(nodes);
            $scope.alchemy.remove.edges(edges);
            //
            // $scope.alchemy.a.remove.allNodes("all");
            // $scope.alchemy.a.remove.allEdges();

            $scope.returneddata = data;
            $scope.some_data = {
                "nodes": data.nodes,
                "edges": data.rels
                //     [{
                //     "id": 290,
                //     "source": 1,
                //     "target": 7,
                //     "value": "By"
                // }]
            }
            ;
            console.log(data, "Got graph data");
            $scope.config = {
                dataSource: $scope.some_data,
                forceLocked: false,
                zoomControls: true,
                initialScale: .25,
                initialTranslate: [250, 200]
                // graphHeight: function() {return $window.innerHeight/2},
                // graphWidth: function() {return $window.innerWidth/4}
            };

            $scope.alchemy = new $window.Alchemy($scope.config);

        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response)
        });

    };
    $scope.testAPI();
    $scope.getUsers();


}
