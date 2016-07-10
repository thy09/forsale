var forsale = {
    sock_init : function(){
        this.sock.on("discussion", function(msg){
            console.log(msg);
            $(".discussion").prepend("<p>"+ unescape(msg.data) +"</p>");
        });
        this.sock.on("open", function(msg){
            console.log(msg);
            $("#w"+msg.data).addClass("open");
            codenames.game.opened[msg.idx] = 1;
        });
    },
    submit_price : function(){
        var price = $("#price").val();
        if (!price){
            alert("请输入价格");
            return;
        }
        price = price / 1000;
        data = {"price":price,"type":"price"};
        postJson("/submit?id="+this.id,data,function(res){
            if (res.status != "success"){
                alert(res.status);
                return;
            }
            location.reload();
        })
    },
    give_up : function(){
        postJson("/submit?id="+this.id,{"type":"giveup"},function(res){
            if (res.status != "success"){
                alert(res.status);
                return;
            }
            location.reload();
        })        
    },
    submit_house : function(){
        var house = $("#my_house").val();
        if (!house){
            alert("请输入价格");
            return;
        }
        postJson("/submit?id="+this.id,{"type":"house","house":house},function(res){
            if (res.status != "success"){
                alert(res.status);
                return;
            }
            location.reload();
        })   
    },
    be_captain : function(){
        if (!confirm("确定是队长？队长会看到答案哦！")){
            return;
        }
        $(".word").addClass("show");
        $(".word").each(function(idx,elm){
            $(elm).click(function(){
                if (!confirm("确定点开 "+this.game.words[idx] + " 这个代号?")){
                    return;
                }
                this.game.opened[idx] = 1;
                var data = {"id":this.game.id,"idx":idx};
                this.sock.emit("open",{"data":data});
            }.bind(this));
        }.bind(this));
        $(".captain").removeClass("hidden");
    },
    submit : function(){
        var name = $("#name").val();
        var sentence = $("#sentence").val();
        if (name == ""){
            alert("请输入姓名");
            return;
        }
        if (sentence == ""){
            alert("请输入发言");
            return;
        }
        var data = {"id":this.game.id,"say":escape(name+": "+sentence)};
        console.log(data);
        this.sock.emit("update",{"data":data});
        $("#sentence").val("");
    },
    sock : null,
}
