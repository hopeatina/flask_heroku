/**
 * Created by Hope on 6/18/2016.
 */
'use strict';   // See note about 'use strict'; below

var myApp = angular.module('myApp', []);

myApp.controller('MyCtrl', MyCtrl)
    .controller('HomeCtrl', HomeCtrl)
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
function HomeCtrl($scope, $window) {
    $scope.q1 = false;
    $scope.q2 = false;
    $scope.q3 = false;
    $scope.q4 = false;
    $scope.q5 = false;
    $scope.q6 = false;

    $scope.switchFaq = function (q) {
        console.log(q);
        q = q ? false : true;
    }
}
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
    $scope.connected = true;
    $scope.selectedCatBool = false;
    $scope.exploretext = "View Messages";
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
    $scope.graphstatebool = false; 

    $scope.switchExplore = function () {
        console.log($scope.connected);
        $scope.connected = true;
        $scope.explorebool = !$scope.explorebool;
        $scope.exploretext = $scope.explorebool ? "View Graph" : "View Messages";
        $scope.explorecurrent = !$scope.explorebool ? "Graph" : "Messages";

    };
    $scope.switchConnect = function () {
        $scope.connected = !$scope.connected;
        console.log($scope.connected)
    };
    $scope.switchCatSelection = function (entity) {
        $scope.selectedCatItem = entity;
        $scope.selectedCatBool = true;
        if (entity.id != -1 && $scope.connected)
            $scope.getGraphData(entity.id);
        else
            $scope.getUserOneData(entity.id);
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
            $scope.currentEntities = [{img: "", name: "All Users", id: -1}];
            console.log(response);
            // $scope.channels.push({img: "None", name: "All Channels"});
            response.data.members.forEach(function (member) {
                $scope.currentEntities.push({img: member.profile.image_24, name: member.name, id: member.id});

            });
            console.log($scope.currentEntities)
        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response)
        });
    };
    $scope.getGraphData = function (entityid) {
        $scope.graphstatebool = true; 
        $http({
            url: '/api/getexploredata',
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(entityid)
        }).success(function (data) {

            if (data == [])
                $scope.graphstatebool = false; 

            var nodes = $scope.alchemy.get.allNodes("all");
            var edges = $scope.alchemy.get.allEdges();

            $scope.alchemy.remove.nodes(nodes);
            $scope.alchemy.remove.edges(edges);
            var iEl = angular.element( document.querySelector( '#alchemy > svg:nth-child(1)' ) );
            iEl.remove();
            // $scope.alchemy.updateGraph();

            

            //
            // $scope.alchemy.a.remove.allNodes("all");
            // $scope.alchemy.a.remove.allEdges();

            var textArray = [
                    'links',
                    'channels',
                    'messages',
                    'users',
                    'tags'
                ];
            $scope.returneddata = data;
            // data.nodes.forEach(function (node) {
            //     var randomNumber = Math.floor(Math.random() * textArray.length);
            //     node.type = textArray[randomNumber]
            // });
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
                initialScale: .8,
                initialTranslate: [100, 100],
                nodeTypes: {
                    "type": ["users",
                        "links",
                        "messages", "channels", "tags"]
                },
                nodeStyle: {
                    "users": {
                        color: "#00ff0e",
                        borderColor: "#D3D3D3"
                    },
                    "links": {
                        color: "#428bca",
                        borderColor: "#D3D3D3"
                    },
                    "messages": {
                        color: "#ff7921",
                        borderColor: "#D3D3D3"
                    },
                    "channels": {
                        color: "#ffffff",
                        borderColor: "#D3D3D3"
                    },
                    "tags": {
                        color: "#d2322d",
                        borderColor: "#D3D3D3"
                    }
                }
                // graphHeight: function() {return $window.innerHeight/2},
                // graphWidth: function() {return $window.innerWidth/4}
            };

            $scope.alchemy = new $window.Alchemy($scope.config);
            console.log($scope.alchemy, $window.Alchemy)

        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response)
        });

    };
    $scope.getUserOneData = function (id) {
        $scope.userOneScore = 23;
        $scope.userOneTags = [
            "Zika", "IBM", "Watson",
            "Awesome", "Sauce", "Juice",
            "Chicken", "Rice", "Fufu",
            "Orange Soda", "Tech", "Life"
        ];
    };



    $scope.testAPI();
    $scope.getUsers();


}
